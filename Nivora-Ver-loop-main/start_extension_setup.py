#!/usr/bin/env python3
"""
Nivora Extension Setup Script
=============================

This script starts both the token server and agent to work with the browser extension.

Usage:
    python start_extension_setup.py

What it does:
1. Starts the token server on port 8080 (matches extension expectation)
2. Provides instructions to start the agent and build the extension
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def main():
    print("🚀 Nivora Extension Setup")
    print("=" * 50)

    # Check if we're in the right directory
    current_dir = Path.cwd()
    if not (current_dir / "agent.py").exists():
        print("❌ Please run this script from the Nivora main directory")
        print("   (where agent.py is located)")
        return

    print("📡 Starting token server on port 8080...")

    try:
        # Start the token server
        token_server = subprocess.Popen(
            [sys.executable, "Nivora-web-page/token-server-ultimate.py"],
            cwd=current_dir
        )

        print("✅ Token server started!")
        print()
        print("🎯 Next steps:")
        print("   1. In a new terminal, run the agent:")
        print("      python agent.py")
        print()
        print("   2. In another terminal, build the extension:")
        print(f"      cd \"{current_dir / 'nivora-extension'}\"")
        print("      npm install")
        print("      npm run build")
        print()
        print("   3. Load the extension in Chrome:")
        print("      - Go to chrome://extensions/")
        print("      - Enable Developer mode")
        print(f"      - Click 'Load unpacked' and select: {current_dir / 'nivora-extension' / 'dist'}")
        print()
        print("🔄 Press Ctrl+C to stop the token server")

        # Keep the token server running
        token_server.wait()

    except KeyboardInterrupt:
        print("\n\n🛑 Stopping token server...")
        token_server.terminate()
        token_server.wait()
        print("✅ Token server stopped.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()