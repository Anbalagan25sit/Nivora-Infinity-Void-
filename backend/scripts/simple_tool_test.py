"""
Simple Tool Test - Universal Web Agent Recognition
=================================================
"""

def test_tools():
    try:
        from tools import ALL_TOOLS
        from universal_web_tools import automate_website_task
        print(f"SUCCESS: Tools loaded - {len(ALL_TOOLS)} total tools")
        print(f"SUCCESS: Universal Web Agent available: {automate_website_task in ALL_TOOLS}")

        # Check tool names
        tool_names = []
        for tool in ALL_TOOLS:
            if hasattr(tool, 'name'):
                tool_names.append(tool.name)
            elif hasattr(tool, '__name__'):
                tool_names.append(tool.__name__)

        universal_tools = [name for name in tool_names if 'automate' in name.lower()]
        print(f"Universal Web Agent tools found: {universal_tools}")

        if len(universal_tools) >= 3:
            print("RESULT: Universal Web Agent tools are properly loaded!")
            print("The agent should be able to handle:")
            print("- 'Go to GitHub and tell me what repos are there'")
            print("- 'Visit LinkedIn and check messages'")
            print("- 'Search Amazon for laptops under $1000'")
            return True
        else:
            print("WARNING: Universal Web Agent tools may not be fully loaded")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_tools()
    if success:
        print("\nCONCLUSION: Tools are ready. If agent still refuses,")
        print("the issue is likely in prompt instructions or agent selection.")
    else:
        print("\nCONCLUSION: Tool loading issues detected.")