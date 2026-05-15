import asyncio
import logging
from collections import namedtuple
import os
from dotenv import load_dotenv

load_dotenv()

# Force AWS backend
os.environ["COMPUTER_USE_BACKEND"] = "aws"

from youtube_automation import youtube_search_and_play

logging.basicConfig(level=logging.INFO)

# Mock context for the tool
MockContext = namedtuple('MockContext', ['room'])
ctx = MockContext(None)

async def main():
    print(f"AWS Region: {os.getenv('AWS_REGION')}")
    print(f"Has Access Key: {bool(os.getenv('AWS_ACCESS_KEY_ID'))}")
    print(f"Computer Use Backend: {os.getenv('COMPUTER_USE_BACKEND')}")
    
    print("Executing YouTube search and play using AWS Nova Pro...")
    result = await youtube_search_and_play(ctx, "mr ig ets2 latest video", prefer_live=False)
    print("\nResult:", result)

if __name__ == "__main__":
    asyncio.run(main())
