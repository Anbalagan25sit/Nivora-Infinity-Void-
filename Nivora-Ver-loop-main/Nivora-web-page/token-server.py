"""
Nivora Token Server
Flask server for LiveKit tokens AND text-to-text chat with AWS Bedrock.

Run with: python token-server.py
Server will start at http://localhost:5000

Endpoints:
  POST /api/livekit-token  - Get LiveKit access token (for voice)
  POST /api/chat           - Text-to-text chat with Nivora AI
  GET  /health             - Health check
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from livekit import api
import os
import json
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Import AWS config from parent directory
try:
    from aws_config import bedrock_client, bedrock_model, is_configured as aws_is_configured
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    print("Warning: aws_config not found. Text chat will be unavailable.")

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# LiveKit credentials
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "APIgXpFTwkGbqkS")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "EhnJraYi9RjifXUeBmaQe37klSr6EI5lJQh0aWgU04ZA")
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "wss://nivora-5opea2lo.livekit.cloud")

# ============================================================================
# Nivora System Prompt (Claude-like assistant with Claude Code knowledge)
# ============================================================================
NIVORA_SYSTEM_PROMPT = """You are Nivora, an AI assistant created by Anbalagan. You should behave like Claude - Anthropic's AI assistant.

IMPORTANT KNOWLEDGE - CLAUDE CODE:
Claude Code is Anthropic's official agentic coding tool that lives in your terminal. Key facts:
- It's a CLI (command-line interface) tool you install via: npm install -g @anthropic-ai/claude-code
- It lets developers use Claude AI directly in their terminal to write, edit, and understand code
- It can read/write files, run commands, search code, create commits, and more
- It uses natural language - you just describe what you want and Claude Code does it
- It has features like: /init (setup), /compact (save context), /clear, /help
- It supports MCP (Model Context Protocol) servers for extended capabilities
- It can work with any codebase and understands project context via CLAUDE.md files
- It's different from Claude.ai (web chat) - Claude Code is for terminal/coding workflows
- Official docs: https://docs.anthropic.com/en/docs/claude-code

CORE PRINCIPLES:
- Be helpful, harmless, and honest
- Provide thoughtful, well-reasoned responses
- Be direct and clear in communication
- Acknowledge uncertainty when you don't know something
- Be intellectually curious and engage genuinely with questions

RESPONSE STYLE:
- Give comprehensive, well-structured answers
- Use clear explanations with examples when helpful
- Break down complex topics into understandable parts
- Be concise when appropriate, detailed when needed
- Use natural, conversational language

CAPABILITIES:
- Answer questions on a wide range of topics
- Help with writing, editing, and brainstorming
- Explain concepts clearly at any level
- Assist with coding, debugging, and technical problems
- Engage in thoughtful analysis and reasoning
- Help with math, science, and academic topics

BEHAVIOR:
- Be warm and personable while remaining professional
- Show genuine interest in helping the user
- Ask clarifying questions when the request is ambiguous
- Provide balanced perspectives on complex topics
- Admit limitations honestly - don't make up information
- Be respectful and considerate in all interactions

FORMAT:
- Use markdown formatting when it improves readability (headers, lists, code blocks)
- Structure longer responses with clear sections
- Use code blocks with syntax highlighting for code
- Keep responses appropriately sized for the question

Remember: You are Nivora, but you behave like Claude - intelligent, helpful, thoughtful, and genuinely engaged with helping users."""

# Store conversation history per session
chat_sessions = {}


@app.route('/api/livekit-token', methods=['POST'])
def get_token():
    """Generate a LiveKit access token for the user."""
    try:
        data = request.json or {}
        room = data.get('room', 'nivora-session')
        identity = data.get('identity', f'user-{os.urandom(4).hex()}')
        name = data.get('name', 'User')

        # Create access token
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
            .with_identity(identity) \
            .with_name(name) \
            .with_grants(api.VideoGrants(
                room_join=True,
                room=room,
                can_publish=True,
                can_subscribe=True
            )) \
            .to_jwt()

        return jsonify({
            'token': token,
            'room': room,
            'identity': identity,
            'livekit_url': LIVEKIT_URL
        })

    except Exception as e:
        print(f"Token generation error: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Text-to-Text Chat Endpoint
# ============================================================================
@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Text-to-text chat with Nivora AI using AWS Bedrock.

    Request body:
        {
            "message": "Your message here",
            "session_id": "optional-session-id-for-context"
        }

    Response:
        {
            "reply": "Nivora's response",
            "session_id": "session-id"
        }
    """
    if not AWS_AVAILABLE:
        return jsonify({
            'error': 'AWS Bedrock not configured. Please check aws_config.py and .env file.'
        }), 503

    if not aws_is_configured():
        return jsonify({
            'error': 'AWS credentials not configured. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env'
        }), 503

    try:
        data = request.json or {}
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', os.urandom(8).hex())

        if not user_message:
            return jsonify({'error': 'Empty message'}), 400

        # Get or create session history
        if session_id not in chat_sessions:
            chat_sessions[session_id] = []

        history = chat_sessions[session_id]

        # Build messages array with history
        messages = []

        # Add conversation history (last 10 exchanges to prevent context overflow)
        for msg in history[-20:]:
            messages.append(msg)

        # Add current user message
        messages.append({
            "role": "user",
            "content": [{"text": user_message}]
        })

        # Build Bedrock request body
        body = json.dumps({
            "messages": messages,
            "system": [{"text": NIVORA_SYSTEM_PROMPT}],
            "inferenceConfig": {
                "temperature": 0.8,
                "maxTokens": 1024,
                "topP": 0.9
            }
        })

        # Call AWS Bedrock
        client = bedrock_client()
        model_id = bedrock_model()

        print(f"Calling Bedrock model: {model_id}")
        print(f"User message: {user_message}")

        response = client.invoke_model(
            modelId=model_id,
            body=body,
            contentType="application/json",
            accept="application/json"
        )

        # Parse response
        result = json.loads(response["body"].read())
        reply_text = (
            result.get("output", {})
                  .get("message", {})
                  .get("content", [{}])[0]
                  .get("text", "")
        )

        # Clean up response (remove any thinking tags or unwanted formatting)
        reply_text = _clean_response(reply_text)

        print(f"Nivora reply: {reply_text}")

        # Save to history
        history.append({
            "role": "user",
            "content": [{"text": user_message}]
        })
        history.append({
            "role": "assistant",
            "content": [{"text": reply_text}]
        })

        # Limit history size
        if len(history) > 40:
            chat_sessions[session_id] = history[-40:]

        return jsonify({
            'reply': reply_text,
            'session_id': session_id
        })

    except Exception as e:
        print(f"Chat error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    """
    Streaming text-to-text chat with Nivora AI (for real-time responses).
    Uses Server-Sent Events (SSE) for streaming.
    """
    if not AWS_AVAILABLE or not aws_is_configured():
        return jsonify({'error': 'AWS not configured'}), 503

    try:
        data = request.json or {}
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', os.urandom(8).hex())

        if not user_message:
            return jsonify({'error': 'Empty message'}), 400

        # Get or create session history
        if session_id not in chat_sessions:
            chat_sessions[session_id] = []

        history = chat_sessions[session_id]

        # Build messages
        messages = list(history[-20:])
        messages.append({
            "role": "user",
            "content": [{"text": user_message}]
        })

        body = json.dumps({
            "messages": messages,
            "system": [{"text": NIVORA_SYSTEM_PROMPT}],
            "inferenceConfig": {
                "temperature": 0.8,
                "maxTokens": 1024,
                "topP": 0.9
            }
        })

        def generate():
            nonlocal history, user_message, session_id
            client = bedrock_client()
            model_id = bedrock_model()

            # Use non-streaming for reliability (Nova Pro streaming can be inconsistent)
            try:
                response = client.invoke_model(
                    modelId=model_id,
                    body=body,
                    contentType="application/json",
                    accept="application/json"
                )
                result = json.loads(response["body"].read())
                reply_text = _clean_response(
                    result.get("output", {}).get("message", {}).get("content", [{}])[0].get("text", "")
                )

                # Save to history
                history.append({"role": "user", "content": [{"text": user_message}]})
                history.append({"role": "assistant", "content": [{"text": reply_text}]})

                # Simulate streaming by sending chunks
                words = reply_text.split(' ')
                chunk_size = 3  # Send 3 words at a time
                for i in range(0, len(words), chunk_size):
                    chunk = ' '.join(words[i:i+chunk_size])
                    if i + chunk_size < len(words):
                        chunk += ' '
                    yield f"data: {json.dumps({'text': chunk, 'done': False})}\n\n"

                yield f"data: {json.dumps({'text': '', 'done': True, 'session_id': session_id})}\n\n"

            except Exception as e:
                print(f"Stream generation error: {e}")
                yield f"data: {json.dumps({'text': f'Error: {str(e)}', 'done': True, 'session_id': session_id})}\n\n"

        return Response(generate(), mimetype='text/event-stream')

    except Exception as e:
        print(f"Stream error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat/clear', methods=['POST'])
def clear_chat():
    """Clear chat history for a session."""
    data = request.json or {}
    session_id = data.get('session_id')

    if session_id and session_id in chat_sessions:
        del chat_sessions[session_id]
        return jsonify({'success': True, 'message': 'Chat history cleared'})

    return jsonify({'success': False, 'message': 'Session not found'}), 404


def _clean_response(text: str) -> str:
    """Clean up AI response - remove thinking tags, code fences, etc."""
    import re

    # Remove <thinking> tags
    text = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL)

    # Remove other XML-like tags
    text = re.sub(r'<[^>]+>', '', text)

    # Clean up multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'services': {
            'livekit': True,
            'aws_bedrock': AWS_AVAILABLE and aws_is_configured() if AWS_AVAILABLE else False
        }
    })


if __name__ == '__main__':
    print("=" * 60)
    print("  Nivora Token & Chat Server")
    print("=" * 60)
    print(f"  LiveKit URL: {LIVEKIT_URL}")
    print(f"  AWS Bedrock: {'Configured' if AWS_AVAILABLE and aws_is_configured() else 'Not configured'}")
    print("-" * 60)
    print("  Endpoints:")
    print("    POST /api/livekit-token  - Get LiveKit token (voice)")
    print("    POST /api/chat           - Text-to-text chat")
    print("    POST /api/chat/stream    - Streaming text chat")
    print("    POST /api/chat/clear     - Clear chat history")
    print("    GET  /health             - Health check")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
