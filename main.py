import os
import json
import httpx
import asyncio
from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import Response
from dotenv import load_dotenv

from twilio.twiml.voice_response import VoiceResponse
from google import genai
from google.genai import types

load_dotenv()

app = FastAPI()

# Initialize AI Client
ai_client = genai.Client()

# ---------------------------------------------------------------------------
# 1. The Call Intake (Twilio Webhook)
# ---------------------------------------------------------------------------
@app.post("/incoming-call")
async def handle_incoming_call(request: Request):
    """Twilio hits this endpoint the moment the phone rings."""
    response = VoiceResponse()
    
    greeting = (
        "Hi, I’m Kundavai, the AI assistant for Deepak. "
        "Go ahead and leave a brief message with your name and number. "
        "If it’s urgent please text Deepak."
    )
    response.say(greeting, voice="Polly.Aditi")
    
    response.record(
        max_length=20,
        play_beep=True,
        action="/process-voicemail" 
    )
    
    response.hangup()
    return Response(content=str(response), media_type="text/xml")

# ---------------------------------------------------------------------------
# 2. The Audio Processing & Telegram (Background Task)
# ---------------------------------------------------------------------------
async def analyze_and_notify(recording_url: str, caller_phone: str):
    """Downloads audio, evaluates with Gemini, and alerts via Telegram."""
    print(f"📥 Downloading voicemail from: {caller_phone}")
    
    await asyncio.sleep(2) # Give Twilio a moment to save the file
    
    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
    
    async with httpx.AsyncClient(follow_redirects=True) as http_client:
        
        # --- 1. Download Audio ---
        audio_response = await http_client.get(
            recording_url + ".wav",
            auth=(twilio_sid, twilio_token)
        )
        
        if audio_response.status_code != 200:
            print(f"❌ Error downloading audio! HTTP {audio_response.status_code}")
            return
            
        audio_bytes = audio_response.content
        print(f"✅ Audio downloaded successfully: {len(audio_bytes)} bytes")

        # --- 2. Gemini Evaluation ---
        evaluation_schema = types.Schema(
            type="OBJECT",
            properties={
                "status": types.Schema(type="STRING", description="Must be either 'spam' or 'legit'"),
                "caller_name": types.Schema(type="STRING", description="The name given, or 'Unknown'"),
                "callback_number": types.Schema(type="STRING", description="The number given, or 'Unknown'"),
                "summary": types.Schema(type="STRING", description="A brief summary of the message")
            },
            required=["status", "caller_name", "callback_number", "summary"]
        )

        print("🧠 Sending audio to Gemini for evaluation...")
        prompt = (
            "Listen to this voicemail. Evaluate if the caller is a bot, a telemarketer, or a legitimate person "
            "leaving a message. If it is spam, a sales pitch, or empty dead air, mark status as 'spam'. "
            "If it is legitimate, mark status as 'legit' and extract the details."
        )
        
        gemini_response = ai_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"),
                prompt
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=evaluation_schema,
                temperature=0.1
            )
        )
        
        decision = json.loads(gemini_response.text)
        print(f"📋 Gemini Decision: {decision}")
        
        # --- 3. Telegram Notification ---
        status = decision.get("status", "unknown")
        caller_name = decision.get("caller_name", "Unknown")
        summary = decision.get("summary", "No summary provided")
        
        # Determine Header based on status
        if status == "legit":
            header = "📞 *New Voicemail Alert*"
        else:
            header = "🚫 *Likely Spam Detected*"

        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        message_text = (
            f"{header}\n\n"
            f"*Caller:* {caller_name}\n"
            f"*Phone:* {caller_phone}\n\n"
            f"*Summary:*\n{summary}"
        )
        
        payload = {
            "chat_id": chat_id,
            "text": message_text,
            "parse_mode": "Markdown"
        }
        
        tg_response = await http_client.post(telegram_url, json=payload)
        
        if tg_response.status_code == 200:
            print(f"✅ Telegram alert sent successfully ({status})!")
        else:
            print(f"❌ Failed to send Telegram alert: {tg_response.text}")

# ---------------------------------------------------------------------------
# 3. The Voicemail Hand-off Endpoint
# ---------------------------------------------------------------------------
@app.post("/process-voicemail")
async def process_voicemail(
    request: Request, 
    background_tasks: BackgroundTasks,
    RecordingUrl: str = Form(...),
    From: str = Form(...)
):
    background_tasks.add_task(analyze_and_notify, RecordingUrl, From)
    
    response = VoiceResponse()
    response.say("Your message has been sent. Goodbye.", voice="Polly.Aditi")
    response.hangup()
    
    return Response(content=str(response), media_type="text/xml")