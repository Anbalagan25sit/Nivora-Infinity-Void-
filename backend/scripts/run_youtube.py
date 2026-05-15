import asyncio
import logging
from collections import namedtuple
from youtube_automation import play_youtube_quick
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

# Mock context for the tool
MockContext = namedtuple('MockContext', ['room'])
ctx = MockContext(None)

async def main():
    print("Executing YouTube search and play using AWS Nova Pro...")
    result = await play_youtube_quick("mr ig ets2", ctx)
    print("\nResult:", result)

if __name__ == "__main__":
    asyncio.run(main())
