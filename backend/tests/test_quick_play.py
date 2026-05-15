import asyncio
from collections import namedtuple
from youtube_automation import play_youtube_quick
import pyautogui

pyautogui.FAILSAFE = False

MockContext = namedtuple('MockContext', ['room'])

async def test():
    print("Testing updated play tool...")
    res = await play_youtube_quick("mutta kalaki song", MockContext(None))
    print(res)

if __name__ == "__main__":
    asyncio.run(test())
