# Nivora-Ver-loop

# 🧠 Friday - Your Personal AI Assistant (AWS Edition)

This is a Python-based AI assistant inspired by *Jarvis*, now fully powered by **AWS**, capable of:

- 🔍 Searching the web  
- 🌤️ Weather checking
- 📨 Sending Emails (Amazon SES)
- 🧠 LLM via Amazon Bedrock (Claude)
- 🗣️ Speech-to-Text via Amazon Transcribe
- 🔊 Text-to-Speech via Amazon Polly
- 📸 Screenshots uploaded to Amazon S3
- 📋 Habit tracking via Amazon DynamoDB
- 🎵 Spotify playback control

This agent uses LiveKit for real-time voice communication.

---

## 📽️ Tutorial Video

Before you start, **make sure to follow this tutorial to set up the voice agent correctly**:  
🎥 [Watch here](https://youtu.be/An4NwL8QSQ4?si=v1dNDDonmpCG1Els)

---

## 🚀 Setup

1. Create a Python virtual environment and activate it
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your keys (see below)
4. Set up your LiveKit account and configure `LIVEKIT_URL` and `LIVEKIT_API_SECRET`
5. Run the agent:
   ```bash
   python agent.py dev
   ```

---

## 🔑 Required Environment Variables (.env)

### AWS Credentials (required for all AWS services)
```
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
```

### AWS Bedrock (LLM)
```
AWS_BEDROCK_MODEL=anthropic.claude-sonnet-4-20250514
```
> Ensure the model is enabled in your Bedrock console for your region.

### Amazon Polly (TTS)
```
AWS_POLLY_VOICE=Matthew
```
> Other voices: Joanna, Amy, Brian, Ivy, etc. Use `neural` engine voices for best quality.

### Amazon SES (Email)
```
AWS_SES_SENDER_EMAIL=you@example.com
```
> The sender email must be **verified** in SES. If in sandbox mode, recipient emails must also be verified.

### Amazon S3 (Screenshots & Email Storage)
```
AWS_S3_BUCKET=nivora-bucket
```
> Create the bucket in your AWS console. For email reading, set up SES receiving rules to deliver to `s3://your-bucket/emails/inbox/`.

### Amazon DynamoDB (Habit Tracking)
```
AWS_DYNAMODB_TABLE=nivora_habits
```
> Create a DynamoDB table with partition key `pk` (String) and sort key `sk` (String).

### LiveKit
```
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...
```

### Spotify (optional)
```
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...
SPOTIFY_REFRESH_TOKEN=...
```
> Run `python get_spotify_token.py` to get the refresh token.

---

## 🏗️ AWS Services Used

| Service | Purpose |
|---------|---------|
| **Amazon Bedrock** | LLM (Claude) for conversation and reasoning |
| **Amazon Transcribe** | Real-time speech-to-text |
| **Amazon Polly** | Neural text-to-speech |
| **Amazon SES** | Sending emails |
| **Amazon S3** | Screenshot storage, email inbox |
| **Amazon DynamoDB** | Habit tracking persistence |

---

## 📁 Project Structure

```
agent.py          — LiveKit agent entry point (Bedrock + Polly + Transcribe)
aws_config.py     — Centralized AWS boto3 client factory
tools.py          — 20+ tools (SES email, DynamoDB habits, S3 screenshots, etc.)
prompts.py        — Structured prompt builder
spotify_api.py    — Spotify Web API client
get_spotify_token.py — One-time Spotify OAuth setup
requirements.txt  — Python dependencies
```


## ??? New Features Setup (Google & Spotify)

### 1. Spotify
- Ensure SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, and SPOTIFY_REFRESH_TOKEN are in your .env file.
- spotify_api.py handles authentication refresh.

### 2. Google Sheets & Calendar
- **Sheets**: Place your service account JSON file as gcp-credentials.json in the root (or set GOOGLE_APPLICATION_CREDENTIALS env var).
- **Calendar**: Place your 	oken.json (generated from OAuth flow) in the root directory.

### 3. Email
- Set EMAIL_USER (your gmail) and EMAIL_PASS (App Password) in .env.

### 4. Dependencies
- Run pip install -r requirements.txt to install new libraries (gspread, google-api-python-client, pywhatkit, etc.).

