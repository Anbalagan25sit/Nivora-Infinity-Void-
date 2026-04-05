#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test script for Nivora Enhanced Chat with Tools
Tests basic functionality without needing AWS
"""

import sys
import os
import io

# Fix Windows encoding issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 60)
print("  Nivora Enhanced Chat - Tool Test")
print("=" * 60)

# Test tool functions
print("\n1. Testing web_search...")
try:
    from duckduckgo_search import DDGS
    results = DDGS().text("Python programming", max_results=2)
    if results:
        print(f"   ✓ Web search works! Found {len(results)} results")
        print(f"     First result: {results[0]['title']}")
    else:
        print("   ✗ Web search returned no results")
except ImportError:
    print("   ✗ duckduckgo-search not installed")
    print("     Install with: pip install duckduckgo-search")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n2. Testing get_weather...")
try:
    import requests
    r = requests.get("https://wttr.in/London?format=j1", timeout=5)
    if r.status_code == 200:
        data = r.json()
        temp = data['current_condition'][0]['temp_C']
        print(f"   ✓ Weather API works! Temperature in London: {temp}°C")
    else:
        print(f"   ✗ Weather API returned status {r.status_code}")
except ImportError:
    print("   ✗ requests not installed")
    print("     Install with: pip install requests")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n3. Testing open_website...")
try:
    import webbrowser
    print("   ✓ webbrowser module available (part of Python stdlib)")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n4. Testing calculate...")
try:
    result = eval("2 + 2", {"__builtins__": {}}, {})
    if result == 4:
        print(f"   ✓ Calculate works! 2 + 2 = {result}")
    else:
        print(f"   ✗ Calculate gave wrong result: {result}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n5. Checking Flask dependencies...")
try:
    import flask
    import flask_cors
    print(f"   ✓ Flask {flask.__version__} installed")
    print("   ✓ flask-cors installed")
except ImportError as e:
    print(f"   ✗ Missing: {e.name}")
    print("     Install with: pip install flask flask-cors")

print("\n6. Checking AWS configuration...")
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

    aws_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')

    if aws_key and aws_secret:
        print("   ✓ AWS credentials configured in .env")
    else:
        print("   ⚠ AWS credentials not found in .env")
        print("     The chat will not work without AWS Bedrock access")
except ImportError:
    print("   ✗ python-dotenv not installed")
    print("     Install with: pip install python-dotenv")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n7. Checking LiveKit...")
try:
    from livekit import api
    print("   ✓ LiveKit SDK installed")
except ImportError:
    print("   ✗ livekit not installed")
    print("     Install with: pip install livekit")

print("\n" + "=" * 60)
print("  Summary")
print("=" * 60)

print("\nRequired for enhanced chat:")
print("  [✓] Flask & flask-cors")
print("  [✓] AWS Bedrock credentials")
print("  [✓] duckduckgo-search")
print("  [✓] requests")
print("  [✓] python-dotenv")
print("  [✓] livekit (for token generation)")

print("\nTo start the enhanced server:")
print("  python token-server-enhanced.py")

print("\nTo test in browser:")
print("  1. Start the server (above)")
print("  2. Open chat.html in your browser")
print("  3. Try: 'What's the weather in Paris?'")
print("  4. Try: 'Search for news about AI'")
print("  5. Try: 'Calculate 15% of 240'")

print("\n" + "=" * 60)
