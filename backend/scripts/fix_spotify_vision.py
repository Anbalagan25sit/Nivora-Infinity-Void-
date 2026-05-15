import asyncio
from collections import namedtuple
from tools import spotify_play
import logging
logging.basicConfig(level=logging.INFO)
MockContext = namedtuple('MockContext', ['room'])

async def test():
    res = await spotify_play(MockContext(None), "mutta kalaki")
    print(res)

if __name__ == "__main__":
    asyncio.run(test())
