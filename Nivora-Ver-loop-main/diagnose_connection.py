#!/usr/bin/env python3
"""
Nivora Connection Diagnostic Tool
================================

This script helps diagnose connection issues between the extension and agent.
"""

import os
import sys
import requests
import json
from pathlib import Path

def check_environment():
    """Check if required environment variables are set."""
    print("Checking Environment Variables...")
    print("=" * 50)

    required_vars = [
        'LIVEKIT_API_KEY',
        'LIVEKIT_API_SECRET',
        'LIVEKIT_URL',
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'GROQ_API_KEY'
    ]

    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'KEY' in var or 'SECRET' in var:
                display_value = value[:8] + "..." if len(value) > 8 else "***"
            else:
                display_value = value
            print(f"✅ {var} = {display_value}")
        else:
            print(f"❌ {var} = NOT SET")
            missing.append(var)

    if missing:
        print(f"\n❌ Missing environment variables: {', '.join(missing)}")
        return False
    else:
        print("\n✅ All required environment variables are set")
        return True

def check_token_server():
    """Test if token server is running and responding."""
    print("\nChecking Token Server...")
    print("=" * 50)

    try:
        response = requests.get(
            "http://localhost:8080/api/token",
            params={"room": "test-room", "participant": "test-user"},
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            print("✅ Token server is running on port 8080")
            print(f"✅ Token generated: {data.get('token', 'N/A')[:20]}...")
            print(f"✅ Room: {data.get('room', 'N/A')}")
            print(f"✅ Participant: {data.get('participant', 'N/A')}")
            return True
        else:
            print(f"❌ Token server returned status {response.status_code}")
            print(f"❌ Response: {response.text}")
            return False

    except requests.ConnectionError:
        print("❌ Cannot connect to token server on localhost:8080")
        print("❌ Make sure to run: python Nivora-web-page/token-server-ultimate.py")
        return False
    except Exception as e:
        print(f"❌ Token server error: {e}")
        return False

def check_livekit_connectivity():
    """Test LiveKit cloud connectivity."""
    print("\nChecking LiveKit Connectivity...")
    print("=" * 50)

    livekit_url = os.getenv('LIVEKIT_URL', '')
    if not livekit_url:
        print("❌ LIVEKIT_URL not set")
        return False

    print(f"LiveKit URL: {livekit_url}")

    # Test basic connectivity (just URL format and reachability)
    if livekit_url.startswith('wss://') or livekit_url.startswith('ws://'):
        # Convert to HTTP for basic connectivity test
        test_url = livekit_url.replace('wss://', 'https://').replace('ws://', 'http://')
        try:
            # Try to reach the domain (won't work for WebSocket endpoint, but tests connectivity)
            import socket
            from urllib.parse import urlparse
            parsed = urlparse(test_url)
            host = parsed.netloc

            # Test DNS resolution and basic connectivity
            socket.gethostbyname(host.split(':')[0])
            print(f"✅ LiveKit domain {host} is reachable")
            return True
        except Exception as e:
            print(f"❌ Cannot reach LiveKit domain: {e}")
            return False
    else:
        print("❌ Invalid LiveKit URL format (should start with wss:// or ws://)")
        return False

def check_extension_build():
    """Check if extension is properly built."""
    print("\nChecking Extension Build...")
    print("=" * 50)

    extension_dir = Path("nivora-extension")
    dist_dir = extension_dir / "dist"

    required_files = [
        "manifest.json",
        "index.html",
        "assets/popup.js",
        "assets/popup.css"
    ]

    if not dist_dir.exists():
        print("❌ Extension not built - 'dist' directory missing")
        print("❌ Run: build_extension.bat (or npm run build in nivora-extension/)")
        return False

    missing_files = []
    for file_path in required_files:
        if not (dist_dir / file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path} exists")

    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False

    # Check manifest content
    try:
        manifest_path = dist_dir / "manifest.json"
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)

        popup_file = manifest.get('action', {}).get('default_popup')
        if popup_file == "index.html":
            print("✅ Manifest popup reference is correct")
        else:
            print(f"❌ Manifest popup reference is wrong: {popup_file} (should be index.html)")

        csp = manifest.get('content_security_policy', {}).get('extension_pages', '')
        if 'localhost' in csp and 'livekit.cloud' in csp:
            print("✅ Content Security Policy allows required connections")
        else:
            print("❌ Content Security Policy may be blocking connections")

    except Exception as e:
        print(f"❌ Error reading manifest: {e}")
        return False

    print("✅ Extension build looks good")
    return True

def main():
    print("Nivora Connection Diagnostics")
    print("=" * 60)

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    results = []

    # Run all checks
    results.append(("Environment", check_environment()))
    results.append(("Token Server", check_token_server()))
    results.append(("LiveKit Connectivity", check_livekit_connectivity()))
    results.append(("Extension Build", check_extension_build()))

    print("\nDIAGNOSTIC SUMMARY")
    print("=" * 60)

    all_good = True
    for check_name, status in results:
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {check_name}")
        if not status:
            all_good = False

    print("\nRECOMMENDED ACTIONS")
    print("=" * 60)

    if not results[0][1]:  # Environment
        print("1. Check your .env file has all required variables")
        print("2. Make sure .env is in the project root directory")

    if not results[1][1]:  # Token Server
        print("1. Start token server: python Nivora-web-page/token-server-ultimate.py")
        print("2. Or use the helper: python start_extension_setup.py")

    if not results[2][1]:  # LiveKit
        print("1. Check your LiveKit credentials in .env")
        print("2. Verify your LiveKit project is active")
        print("3. Test LiveKit URL in a browser")

    if not results[3][1]:  # Extension
        print("1. Build extension: build_extension.bat")
        print("2. Reload extension in chrome://extensions/")

    if all_good:
        print("All checks passed! Try connecting again.")
        print("\nIf still having issues:")
        print("1. Check browser console (F12) for error messages")
        print("2. Try refreshing the extension popup")
        print("3. Make sure agent.py is also running")
    else:
        print("Fix the issues above and try again.")

if __name__ == "__main__":
    main()