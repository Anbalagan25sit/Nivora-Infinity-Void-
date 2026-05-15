"""
LiveKit Token Server for Nivora Chrome Extension
This server generates JWT tokens for the extension to connect to LiveKit rooms.
"""

import os
import uuid
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import FastAPI, fall back to Flask
try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    USE_FASTAPI = True
except ImportError:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    USE_FASTAPI = False

# LiveKit token generation
try:
    from livekit import api
    HAS_LIVEKIT = True
except ImportError:
    HAS_LIVEKIT = False
    print("Warning: livekit package not installed. Run: pip install livekit")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "")
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "")
DEFAULT_ROOM = "nivora-assistant"

def generate_token(room_name: str, participant_name: str) -> str:
    """Generate a LiveKit JWT token"""
    if not HAS_LIVEKIT:
        raise Exception("LiveKit SDK not installed")

    if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        raise Exception("LiveKit API credentials not configured")

    # Create token with permissions
    token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    token.with_identity(participant_name)
    token.with_name(participant_name)

    # Grant permissions
    grant = api.VideoGrants(
        room_join=True,
        room=room_name,
        can_publish=True,
        can_subscribe=True,
        can_publish_data=True,
    )
    token.with_grants(grant)

    # Set TTL using timedelta (fixes the datetime + int error)
    token.with_ttl(timedelta(hours=1))

    return token.to_jwt()


if USE_FASTAPI:
    # FastAPI implementation
    app = FastAPI(title="Nivora Token Server")

    # Enable CORS for Chrome extension
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        return {
            "service": "Nivora Token Server",
            "status": "running",
            "livekit_configured": bool(LIVEKIT_API_KEY and LIVEKIT_API_SECRET),
            "livekit_url": LIVEKIT_URL,
        }

    @app.get("/api/token")
    async def get_token(
        room: str = Query(default=DEFAULT_ROOM, description="Room name"),
        participant: str = Query(default=None, description="Participant name/identity")
    ):
        """Generate a LiveKit access token"""
        try:
            # Generate unique participant name if not provided
            if not participant:
                participant = f"user-{uuid.uuid4().hex[:8]}"

            token = generate_token(room, participant)

            return {
                "token": token,
                "room": room,
                "participant": participant,
                "serverUrl": LIVEKIT_URL,
            }
        except Exception as e:
            logger.error(f"Token generation error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/health")
    async def health():
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "livekit_sdk": HAS_LIVEKIT,
            "credentials_configured": bool(LIVEKIT_API_KEY and LIVEKIT_API_SECRET),
        }

    def run():
        uvicorn.run(app, host="0.0.0.0", port=8080)

else:
    # Flask implementation
    app = Flask(__name__)
    CORS(app)

    @app.route("/")
    def root():
        return jsonify({
            "service": "Nivora Token Server",
            "status": "running",
            "livekit_configured": bool(LIVEKIT_API_KEY and LIVEKIT_API_SECRET),
            "livekit_url": LIVEKIT_URL,
        })

    @app.route("/api/token")
    def get_token():
        """Generate a LiveKit access token"""
        try:
            room = request.args.get("room", DEFAULT_ROOM)
            participant = request.args.get("participant")

            # Generate unique participant name if not provided
            if not participant:
                participant = f"user-{uuid.uuid4().hex[:8]}"

            token = generate_token(room, participant)

            return jsonify({
                "token": token,
                "room": room,
                "participant": participant,
                "serverUrl": LIVEKIT_URL,
            })
        except Exception as e:
            logger.error(f"Token generation error: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/health")
    def health():
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "livekit_sdk": HAS_LIVEKIT,
            "credentials_configured": bool(LIVEKIT_API_KEY and LIVEKIT_API_SECRET),
        })

    def run():
        app.run(host="0.0.0.0", port=8080, debug=True)


if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║              NIVORA TOKEN SERVER                              ║
╠══════════════════════════════════════════════════════════════╣
║  Server URL:    http://localhost:8080                        ║
║  Token API:     http://localhost:8080/api/token              ║
║  Health Check:  http://localhost:8080/api/health             ║
╠══════════════════════════════════════════════════════════════╣
║  LiveKit URL:   {LIVEKIT_URL or 'NOT CONFIGURED':<40} ║
║  Credentials:   {'CONFIGURED' if LIVEKIT_API_KEY else 'MISSING':<40} ║
╚══════════════════════════════════════════════════════════════╝
    """)
    run()
