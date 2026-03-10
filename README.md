
# 📞 Asynchronous AI Call Screener

An intelligent, autonomous call-screening pipeline built for the **Raspberry Pi Zero 2W** using FastAPI, Twilio, and Google's **Gemini 3.1 Flash-Lite**.

Instead of relying on fragile, real-time WebSocket streams, this system acts as an asynchronous gatekeeper. It politely answers unknown calls, records the message, and uses multimodal AI to analyze the raw audio. If the call is legitimate, it sends a summary to **Telegram**; if it's spam, it flags it accordingly while keeping your phone silent.

## ✨ Features

* **Autonomous Background Operation**: Runs as a permanent `systemd` service on Raspberry Pi, independent of any host computer.
* **Ultra-Low Cost (March 2026)**: Utilizes **Gemini 3.1 Flash-Lite**, reducing AI processing costs by **75%** compared to previous generations.
* **Zero-Latency Greeting**: Uses Twilio's **Amazon Polly (Aditi)** neural voice for instant, high-quality interaction.
* **Telegram Integration**: Delivers formatted summaries with distinct headers for "New Voicemail" vs. "Likely Spam."
* **Auto-Cleanup**: Includes an automated Cron job that deletes Twilio recordings every 10 days to maintain a $0.00 storage bill.

## 🏗️ Architecture Flow

1. **The Gateway**: Twilio answers, plays the greeting, and records up to 20 seconds of audio.
2. **The Orchestrator**: Twilio hits the FastAPI `/process-voicemail` webhook. FastAPI acknowledges the request and spins up a background task.
3. **The Brain**: The Pi downloads the `.wav` file and sends it to **Gemini 3.1 Flash-Lite** for strict JSON evaluation (`spam` vs. `legit`).
4. **The Delivery**: FastAPI fires a Telegram Bot API request to your phone with the caller's name, number, and a concise summary.

## 📋 Prerequisites

* **Hardware**: Raspberry Pi Zero 2W (Running Raspberry Pi OS Lite).
* **Services**: Twilio Account (Voice Number), Google Gemini API Key (Tier 1), Telegram Bot Token.
* **Tunneling**: Ngrok with a static domain/URL.

## 🚀 Installation & Setup

1. **Clone & Environment**
```bash
git clone https://github.com/yourusername/ai-call-screener.git
cd ai-call-screener
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn twilio google-genai httpx python-multipart python-dotenv

```


2. **Configure Services**
* Set up `fastapi.service` and `ngrok.service` in `/etc/systemd/system/` for 24/7 autonomy.
* Configure `crontab -e` to run `cleanup_recordings.py` nightly at 3:00 AM.


3. **Deploy**
```bash
sudo systemctl enable fastapi ngrok
sudo systemctl start fastapi ngrok

```



---

Would you like me to add a specific **"Troubleshooting"** section to this README that includes the `journalctl` commands we used to fix the model deprecation issues?
