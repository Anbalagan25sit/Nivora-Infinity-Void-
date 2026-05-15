import asyncio
from collections import namedtuple
from tools import spotify_play
import logging
import pyautogui

logging.basicConfig(level=logging.INFO)
MockContext = namedtuple('MockContext', ['room'])

async def test():
    # If the cursor was in the search bar and hit the "X" button, that's what caused the history delete issue!
    # Let's just use the direct space bar or double click the top result.
    pass

if __name__ == "__main__":
    asyncio.run(test())
