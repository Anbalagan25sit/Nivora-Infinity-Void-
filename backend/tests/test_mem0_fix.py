
import asyncio
from mem0 import AsyncMemoryClient
from dotenv import load_dotenv

load_dotenv(".env")

async def get_all_memories():
    mem0 = AsyncMemoryClient()
    user_name = "Anbu_Infin" # Using the modified name
    try:
        results = await mem0.get_all(user_id=user_name)
        print(f"Success! Found {len(results)} memories.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(get_all_memories())
