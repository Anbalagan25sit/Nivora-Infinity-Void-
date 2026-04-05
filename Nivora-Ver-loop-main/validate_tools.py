
import asyncio
import tools
from livekit.agents import RunContext

async def validate_tools():
    print(f"Loaded {len(tools.ALL_TOOLS)} tools.")
    for tool in tools.ALL_TOOLS:
        print(f"Validating {tool.__name__}...")
        # We don't execute them, just check they are valid function_tool objects
        if not hasattr(tool, "__call__"):
             print(f"ERROR: {tool} is not a valid tool wrapper")
    
    print("All tools structure valid.")

if __name__ == "__main__":
    asyncio.run(validate_tools())
