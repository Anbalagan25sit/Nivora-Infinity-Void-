import asyncio
from collections import namedtuple
from tools import spotify_play
import pyautogui

MockContext = namedtuple('MockContext', ['room'])

async def t():
    await spotify_play(MockContext(None), "mutta kalaki")

if __name__ == "__main__":
    asyncio.run(t())
