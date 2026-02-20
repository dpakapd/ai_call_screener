# 📞 Asynchronous AI Call Screener

An intelligent, asynchronous call-screening pipeline built with FastAPI, Twilio, and Google's Gemini 2.5 Flash. 

Instead of relying on fragile, real-time WebSocket streams that struggle with phone line static and Voice Activity Detection (VAD) latency, this system acts as an asynchronous gatekeeper. It politely answers unknown calls, records the caller's message, and uses multimodal AI to analyze the raw audio file. If the call is a legitimate message, it sends a concise summary to your phone via WhatsApp. If it's a robocall or spam, it silently drops it.

## ✨ Features
* **Zero-Latency Greeting**: Uses Twilio's high-quality Amazon Polly neural voices to instantly greet callers without the lag of real-time AI generation.
* **Multimodal Audio Evaluation**: Feeds the raw `.wav` file directly to Gemini 2.5 Flash, allowing the AI to detect the unnatural cadence, tape hiss, or dead air of automated spam dialers.
* **WhatsApp Integration**: Sends instant, formatted summaries of legitimate voicemails directly to your personal WhatsApp.
* **Cost-Effective**: Eliminates the high API costs of open-ended AI phone conversations. You only pay for a maximum of 20 seconds of audio processing per call.

## 🏗️ Architecture Flow
1. **The Gateway**: Twilio answers the call, plays the greeting, and records up to 20 seconds of audio.
2. **The Orchestrator**: Twilio sends a webhook to the FastAPI backend. FastAPI instantly drops the call to free up the caller, then spins up a background task.
3. **The Brain**: FastAPI downloads the audio and sends it to Gemini 2.5 Flash, forcing a strict JSON evaluation (`spam` vs. `legit`).
4. **The Delivery**: If marked `legit`, FastAPI triggers the Twilio Messaging API to send the caller's name, number, and message summary to your WhatsApp.

## 📋 Prerequisites
* Python 3.11+
* A Twilio Account (with a Voice number and the WhatsApp Sandbox configured)
* A Google Gemini API Key
* [Ngrok](https://ngrok.com/) (for local testing/port forwarding)

## 🚀 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone [https://github.com/yourusername/ai-call-screener.git](https://github.com/yourusername/ai-call-screener.git)
   cd ai-call-screener
