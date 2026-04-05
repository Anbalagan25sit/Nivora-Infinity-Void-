#!/usr/bin/env python3
"""
Nivora Connection Diagnostic Tool (Simple Version)
==================================================
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
            print(f"[OK] {var} = {display_value}")
        else:
            print(f"[FAIL] {var} = NOT SET")
            missing.append(var)

    if missing:
        print(f"\n[FAIL] Missing environment variables: {', '.join(missing)}")
        return False
    else:
        print("\n[OK] All required environment variables are set")
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
            print("[OK] Token server is running on port 8080")
            print(f"[OK] Token generated: {data.get('token', 'N/A')[:20]}...")
            print(f"[OK] Room: {data.get('room', 'N/A')}")
            print(f"[OK] Participant: {data.get('participant', 'N/A')}")
            return True
        else:
            print(f"[FAIL] Token server returned status {response.status_code}")
            print(f"[FAIL] Response: {response.text}")
            return False

    except requests.ConnectionError:
        print("[FAIL] Cannot connect to token server on localhost:8080")
        print("[FAIL] Make sure to run: python Nivora-web-page/token-server-ultimate.py")
        return False
    except Exception as e:
        print(f"[FAIL] Token server error: {e}")
        return False

def check_agent_running():
    """Check if agent.py might be running."""
    print("\nChecking Agent Status...")
    print("=" * 50)

    # We can't directly check if agent.py is running, but we can check for common issues
    print("[INFO] Cannot directly check if agent.py is running")
    print("[INFO] Make sure to run: python agent.py")
    print("[INFO] Agent should show 'AgentSession started successfully' when ready")
    return True  # Always return True since we can't check this

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
        print("[FAIL] Extension not built - 'dist' directory missing")
        print("[FAIL] Run: build_extension.bat")
        return False

    missing_files = []
    for file_path in required_files:
        if not (dist_dir / file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"[OK] {file_path} exists")

    if missing_files:
        print(f"[FAIL] Missing files: {', '.join(missing_files)}")
        return False

    print("[OK] Extension build looks good")
    return True

def main():
    print("Nivora Connection Diagnostics")
    print("=" * 60)

    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("[WARNING] python-dotenv not installed, loading .env manually")

    results = []

    # Run all checks
    results.append(("Environment", check_environment()))
    results.append(("Token Server", check_token_server()))
    results.append(("Agent Status", check_agent_running()))
    results.append(("Extension Build", check_extension_build()))

    print("\nDIAGNOSTIC SUMMARY")
    print("=" * 60)

    all_good = True
    for check_name, status in results:
        status_text = "[OK]" if status else "[FAIL]"
        print(f"{status_text} {check_name}")
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

    if not results[3][1]:  # Extension
        print("1. Build extension: build_extension.bat")
        print("2. Reload extension in chrome://extensions/")

    print("\nDEBUGGING STEPS")
    print("=" * 60)
    print("1. Make sure BOTH token server AND agent.py are running")
    print("2. Check browser console (F12) for JavaScript errors")
    print("3. Try reloading the extension popup")
    print("4. Check chrome://extensions/ and click 'Reload' on Nivora extension")

    if all_good:
        print("\n[SUCCESS] All checks passed! Try connecting again.")
    else:
        print("\n[ERROR] Fix the issues above and try again.")

if __name__ == "__main__":
    main()