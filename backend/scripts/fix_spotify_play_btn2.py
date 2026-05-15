import asyncio
from collections import namedtuple
from tools import spotify_play

MockContext = namedtuple('MockContext', ['room'])

async def t():
    print("Testing Spotify fallback again...")
    await spotify_play(MockContext(None), "mutta kalaki")

if __name__ == "__main__":
    asyncio.run(t())
