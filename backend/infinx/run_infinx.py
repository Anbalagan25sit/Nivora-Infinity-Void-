import asyncio
import argparse
import sys
import os

# Add backend directory to sys.path so imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from infinx.youtube_watcher import InfinxAgent
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

async def main():
    parser = argparse.ArgumentParser(description="Run Infinx Autonomous YouTube Agent")
    parser.add_argument("--url", type=str, default="https://www.youtube.com/watch?v=3A4NvZEG54A", help="YouTube Livestream URL")
    
    args = parser.parse_args()
    
    agent = InfinxAgent(args.url)
    
    try:
        await agent.start()
    except KeyboardInterrupt:
        print("\nStopping Infinx Agent...")
        agent.is_running = False

if __name__ == "__main__":
    asyncio.run(main())
