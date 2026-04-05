"""
Nivora Token Server - ENHANCED with Tools
Flask server for LiveKit tokens AND text-to-text chat with AWS Bedrock + Tool Support.

Run with: python token-server-enhanced.py
Server will start at http://localhost:5000

Endpoints:
  POST /api/livekit-token  - Get LiveKit access token (for voice)
  POST /api/chat           - Text-to-text chat with Nivora AI + Tools
  POST /api/chat/stream    - Streaming text chat with tools
  POST /api/chat/clear     - Clear chat history
  GET  /health             - Health check
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from livekit import api
import os
import json
import sys
import webbrowser
import requests
import datetime

try:
    # Try new package name first
    from ddgs import DDGS
except ImportError:
    try:
        # Fall back to old package name
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None
        print("Warning: Neither 'ddgs' nor 'duckduckgo_search' found. Web search will not work.")
        print("Install with: pip install ddgs")

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
# SIMPLIFIED WEB-COMPATIBLE TOOLS (No RunContext dependency)
# ============================================================================

WEBSITE_MAP = {
    "youtube": "https://www.youtube.com", "github": "https://github.com",
    "google": "https://www.google.com", "gmail": "https://mail.google.com",
    "drive": "https://drive.google.com", "leetcode": "https://leetcode.com",
    "stackoverflow": "https://stackoverflow.com", "reddit": "https://www.reddit.com",
    "twitter": "https://twitter.com", "x": "https://x.com",
    "instagram": "https://www.instagram.com", "linkedin": "https://www.linkedin.com",
    "netflix": "https://www.netflix.com", "spotify": "https://open.spotify.com",
    "chatgpt": "https://chat.openai.com", "claude": "https://claude.ai",
}

def web_search(query: str) -> str:
    """Search the web using DuckDuckGo and return top 5 results."""
    if DDGS is None:
        return "Web search unavailable. Please install: pip install ddgs"

    try:
        results = DDGS().text(query, max_results=5)
        if not results:
            return "No results found."
        formatted = "\n".join([f"• {r['title']}\n  {r['href']}\n  {r.get('body', '')[:150]}..." for r in results])
        return f"Search results for '{query}':\n\n{formatted}"
    except Exception as e:
        return f"Search failed: {str(e)}"

def get_weather(city: str) -> str:
    """Get current weather for a city using wttr.in."""
    try:
        r = requests.get(f"https://wttr.in/{city}?format=j1", timeout=5)
        if r.status_code == 200:
            data = r.json()
            current = data['current_condition'][0]
            temp_c = current['temp_C']
            feels_like = current['FeelsLikeC']
            desc = current['weatherDesc'][0]['value']
            humidity = current['humidity']
            wind = current['windspeedKmph']

            return f"Weather in {city}:\n🌡️ {temp_c}°C (feels like {feels_like}°C)\n☁️ {desc}\n💧 Humidity: {humidity}%\n🌬️ Wind: {wind} km/h"
        return f"Could not get weather for {city}."
    except Exception as e:
        return f"Weather error: {str(e)}"

def open_website(target: str) -> str:
    """Open a website by name or URL."""
    try:
        t = target.strip().lower()
        if t.startswith(("http://", "https://", "www.")):
            url = target if target.startswith(("http://", "https://")) else "https://" + target
            webbrowser.open(url)
            return f"✓ Opened {url}"

        key = t.replace(".com", "").replace(".org", "").replace(" ", "")
        url = WEBSITE_MAP.get(key) or WEBSITE_MAP.get(t) or f"https://www.{key}.com"
        webbrowser.open(url)
        return f"✓ Opened {url}"
    except Exception as e:
        return f"Error opening website: {str(e)}"

def get_current_time() -> str:
    """Get the current time and date."""
    now = datetime.datetime.now()
    return f"Current time: {now.strftime('%I:%M %p')}\nDate: {now.strftime('%A, %B %d, %Y')}"

def calculate(expression: str) -> str:
    """Safely evaluate a mathematical expression."""
    try:
        # Basic safety: only allow numbers and basic operators
        allowed_chars = set('0123456789+-*/()., ')
        if not all(c in allowed_chars for c in expression):
            return "Invalid expression. Only numbers and basic operators (+, -, *, /, parentheses) allowed."

        result = eval(expression, {"__builtins__": {}}, {})
        return f"{expression} = {result}"
    except Exception as e:
        return f"Calculation error: {str(e)}"

# ============================================================================
# TOOL DEFINITIONS FOR AWS BEDROCK
# ============================================================================

TOOLS_SCHEMA = [
    {
        "toolSpec": {
            "name": "web_search",
            "description": "Search the web using DuckDuckGo. Returns top 5 results with titles, URLs, and snippets. Use this when the user asks about current events, news, or information you don't have.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "get_weather",
            "description": "Get current weather information for any city in the world. Returns temperature, conditions, humidity, and wind speed.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "Name of the city (e.g., 'London', 'New York', 'Tokyo')"
                        }
                    },
                    "required": ["city"]
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "open_website",
            "description": "Open a website in the default browser. Can use site names (youtube, github, etc.) or full URLs.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "description": "Website name (e.g., 'youtube', 'github') or full URL (e.g., 'https://example.com')"
                        }
                    },
                    "required": ["target"]
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "get_current_time",
            "description": "Get the current date and time.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "calculate",
            "description": "Perform mathematical calculations. Supports basic arithmetic operations (+, -, *, /, parentheses).",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate (e.g., '2 + 2', '(10 * 5) / 2')"
                        }
                    },
                    "required": ["expression"]
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "play_youtube_video",
            "description": "Search and play a YouTube video in the browser. This is the PRIMARY tool for playing any song or video on YouTube.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search term, song name, or video ID to play"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "show_love_feels",
            "description": "Show how love feels by opening a special Instagram reel. Use this when user asks about 'how love feels', 'what is love like', 'show me love', or similar romantic/love-related questions.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    }
]

# Mock implementation of play_youtube_video for the server if actual module is unavailable
def play_youtube_video(query: str) -> str:
    """Mock implementation of play_youtube_video for the token server"""
    try:
        import urllib.parse
        q = query.strip()
        encoded = urllib.parse.quote(q)
        search_url = f"https://www.youtube.com/results?search_query={encoded}"
        webbrowser.open(search_url)
        return f"Opened YouTube search for '{q}'. (Note: Auto-play requires the full agent.py backend)"
    except Exception as e:
        return f"Failed to open YouTube: {str(e)}"

def show_love_feels() -> str:
    """Show how love feels by opening a specific Instagram reel"""
    try:
        love_reel_url = "https://www.instagram.com/reel/DWaO8ogEzj3/?igsh=MXUyZDA2cTBpdnpzeA=="
        webbrowser.open(love_reel_url)
        return "💕 Opened Instagram reel showing how love feels... ✨"
    except Exception as e:
        return f"Failed to open love reel: {str(e)}"

# Map tool names to functions
TOOL_FUNCTIONS = {
    "web_search": web_search,
    "get_weather": get_weather,
    "open_website": open_website,
    "get_current_time": get_current_time,
    "calculate": calculate,
    "play_youtube_video": play_youtube_video,
    "show_love_feels": show_love_feels
}

# ============================================================================
# Nivora System Prompt (Enhanced with tool awareness)
# ============================================================================
NIVORA_SYSTEM_PROMPT = """You are Nivora, an AI assistant created by Anbalagan. You should behave like Claude - Anthropic's AI assistant.

YOU HAVE ACCESS TO TOOLS! When appropriate, use your tools to help the user:
- web_search: Search the web for current information, news, or facts
- get_weather: Get weather information for any city
- open_website: Open websites in the browser
- get_current_time: Get the current date and time
- calculate: Perform mathematical calculations
- play_youtube_video: Search and play ANY song or video on YouTube
- show_love_feels: Show how love feels with a special visual experience

**LOVE FEELS - SPECIAL TRIGGER:**
When user asks about love feelings, IMMEDIATELY call `show_love_feels()`:
- "how does love feel?" -> show_love_feels()
- "how love feels" -> show_love_feels()
- "what does love feel like?" -> show_love_feels()
- "show me how love feels" -> show_love_feels()
- "what is love like?" -> show_love_feels()
- Any question about the feeling or experience of love -> show_love_feels()

**YOUTUBE PLAYBACK - CRITICAL:**
When user asks to play ANY song/video on YouTube, IMMEDIATELY call `play_youtube_video(query)`:
- "play [song] on youtube" -> play_youtube_video("song name")
- "youtube play [song]" -> play_youtube_video("song name")
- "play [song] youtube" -> play_youtube_video("song name")
- "search and play [song] on yt" -> play_youtube_video("song name")
- "play [song] on yt" -> play_youtube_video("song name")

Use tools proactively when they would be helpful. For example:
- If someone asks "what's the weather in Tokyo?" → use get_weather
- If someone asks "search for news about AI" → use web_search
- If someone asks "open YouTube" → use open_website
- If someone asks "play Shape of You on YouTube" → use play_youtube_video
- If someone asks "what time is it?" → use get_current_time
- If someone asks "what's 15% of 240?" → use calculate

IMPORTANT: Always explain what you're doing when you use a tool. The user will see a nice animation showing the tool being used.

CORE PRINCIPLES:
- Be helpful, harmless, and honest
- Provide thoughtful, well-reasoned responses
- Be direct and clear in communication
- Acknowledge uncertainty when you don't know something
- Use tools to get real-time information when needed

RESPONSE STYLE:
- Give comprehensive, well-structured answers
- Use clear explanations with examples when helpful
- Break down complex topics into understandable parts
- Use markdown formatting when it improves readability
- Be warm and personable while remaining professional

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
# ENHANCED Text-to-Text Chat Endpoint WITH TOOLS
# ============================================================================
@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Text-to-text chat with Nivora AI using AWS Bedrock WITH TOOL SUPPORT.
    """
    if not AWS_AVAILABLE or not aws_is_configured():
        return jsonify({'error': 'AWS Bedrock not configured'}), 503

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

        # Build messages with history
        messages = list(history[-20:])
        messages.append({
            "role": "user",
            "content": [{"text": user_message}]
        })

        client = bedrock_client()
        model_id = bedrock_model()

        # Track tool calls for response
        tool_calls = []
        max_iterations = 5  # Prevent infinite loops
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Build request with tool config
            body = json.dumps({
                "messages": messages,
                "system": [{"text": NIVORA_SYSTEM_PROMPT}],
                "toolConfig": {
                    "tools": TOOLS_SCHEMA
                },
                "inferenceConfig": {
                    "temperature": 0.8,
                    "maxTokens": 2048,
                    "topP": 0.9
                }
            })

            print(f"\n=== Iteration {iteration} ===")
            print(f"Calling Bedrock with {len(messages)} messages")

            response = client.invoke_model(
                modelId=model_id,
                body=body,
                contentType="application/json",
                accept="application/json"
            )

            result = json.loads(response["body"].read())
            output = result.get("output", {})
            message = output.get("message", {})
            content = message.get("content", [])
            stop_reason = result.get("stopReason")

            print(f"Stop reason: {stop_reason}")

            # Add assistant response to messages
            messages.append(message)

            # Check if model wants to use tools
            if stop_reason == "tool_use":
                # Extract tool use requests
                for item in content:
                    if "toolUse" in item:
                        tool_use = item["toolUse"]
                        tool_name = tool_use["name"]
                        tool_input = tool_use["input"]
                        tool_use_id = tool_use["toolUseId"]

                        print(f"Tool requested: {tool_name} with input {tool_input}")

                        # Execute tool
                        tool_func = TOOL_FUNCTIONS.get(tool_name)
                        if tool_func:
                            try:
                                tool_result = tool_func(**tool_input)
                                print(f"Tool result: {tool_result[:100]}...")
                            except Exception as e:
                                tool_result = f"Tool execution error: {str(e)}"
                                print(f"Tool error: {e}")
                        else:
                            tool_result = f"Unknown tool: {tool_name}"

                        # Record tool call for frontend
                        tool_calls.append({
                            "name": tool_name,
                            "input": tool_input,
                            "result": tool_result
                        })

                        # Add tool result back to conversation
                        messages.append({
                            "role": "user",
                            "content": [{
                                "toolResult": {
                                    "toolUseId": tool_use_id,
                                    "content": [{"text": tool_result}]
                                }
                            }]
                        })
                # Continue loop to get final response
                continue

            else:
                # Got final text response
                reply_text = ""
                for item in content:
                    if "text" in item:
                        reply_text += item["text"]

                reply_text = _clean_response(reply_text)
                print(f"Final reply: {reply_text[:100]}...")

                # Save to history (user message + final assistant message)
                history.append({"role": "user", "content": [{"text": user_message}]})
                history.append({"role": "assistant", "content": [{"text": reply_text}]})

                # Limit history size
                if len(history) > 40:
                    chat_sessions[session_id] = history[-40:]

                return jsonify({
                    'reply': reply_text,
                    'session_id': session_id,
                    'tool_calls': tool_calls  # Send tool calls to frontend for animation
                })

        # If we hit max iterations
        return jsonify({
            'reply': "I apologize, but I encountered too many tool calls. Please try rephrasing your request.",
            'session_id': session_id,
            'tool_calls': tool_calls
        })

    except Exception as e:
        print(f"Chat error: {e}")
        import traceback
        traceback.print_exc()
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
    """Clean up AI response - remove thinking tags, etc."""
    import re
    text = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'services': {
            'livekit': True,
            'aws_bedrock': AWS_AVAILABLE and aws_is_configured() if AWS_AVAILABLE else False,
            'tools_available': len(TOOL_FUNCTIONS)
        }
    })


if __name__ == '__main__':
    print("=" * 60)
    print("  Nivora Token & Chat Server (ENHANCED WITH TOOLS)")
    print("=" * 60)
    print(f"  LiveKit URL: {LIVEKIT_URL}")
    print(f"  AWS Bedrock: {'✓ Configured' if AWS_AVAILABLE and aws_is_configured() else '✗ Not configured'}")
    print(f"  Tools Available: {len(TOOL_FUNCTIONS)}")
    print("    - web_search (DuckDuckGo)")
    print("    - get_weather (wttr.in)")
    print("    - open_website (Browser)")
    print("    - get_current_time")
    print("    - calculate")
    print("-" * 60)
    print("  Endpoints:")
    print("    POST /api/livekit-token  - Get LiveKit token (voice)")
    print("    POST /api/chat           - Text-to-text chat WITH TOOLS")
    print("    POST /api/chat/clear     - Clear chat history")
    print("    GET  /health             - Health check")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
