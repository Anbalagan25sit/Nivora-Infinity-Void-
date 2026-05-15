import logging
import subprocess
import json
from livekit.agents import RunContext, function_tool

logger = logging.getLogger(__name__)

def _run_harness(python_code: str) -> str:
    """Helper to run a Python snippet via browser-harness."""
    try:
        # browser-harness accepts code via stdin when piped or using heredocs.
        # We pass the python script via stdin to the subprocess.
        result = subprocess.run(
            "uvx browser-harness",
            shell=True,
            input=python_code,
            text=True,
            capture_output=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"browser-harness error: {e.stderr}")
        return f"Error: {e.stderr.strip()}"
    except Exception as e:
        logger.error(f"Failed to run browser-harness: {e}")
        return f"Error: {str(e)}"

@function_tool()
async def harness_page_info(context: RunContext) -> str:
    """
    Get the current state of the active browser tab (URL, title, dimensions).
    Use this to understand what page you are currently on.
    """
    code = "print(json.dumps(page_info()))"
    return _run_harness(code)

@function_tool()
async def harness_open_url(context: RunContext, url: str) -> str:
    """
    Open a URL in a new tab in the user's running Chrome browser and wait for it to load.
    Always use this when starting a new browser task.
    """
    code = f"""
new_tab({json.dumps(url)})
wait_for_load()
print("Opened and loaded:", {json.dumps(url)})
"""
    return _run_harness(code)

@function_tool()
async def harness_click(context: RunContext, x: int, y: int) -> str:
    """
    Click at specific X, Y coordinates on the current page.
    Get these coordinates by asking the user or inferring from page structure if possible.
    """
    code = f"""
click_at_xy({x}, {y})
print("Clicked at ({x}, {y})")
"""
    return _run_harness(code)

@function_tool()
async def harness_type(context: RunContext, text: str, press_enter: bool = False) -> str:
    """
    Type text into the currently focused input field.
    Make sure to click the input field first before typing.
    Set press_enter=True to submit a form or search after typing.
    """
    enter_code = "press_key('Enter')" if press_enter else ""
    code = f"""
type_text({json.dumps(text)})
{enter_code}
print("Typed text successfully")
"""
    return _run_harness(code)

@function_tool()
async def harness_screenshot(context: RunContext) -> str:
    """
    Take a screenshot of the current page and save it to a temporary file.
    Returns the path to the screenshot image.
    """
    import tempfile
    import os
    path = os.path.join(tempfile.gettempdir(), "harness_screenshot.png")
    # Need to normalize path for python string
    path_str = json.dumps(path)
    code = f"""
path = capture_screenshot({path_str})
print(path)
"""
    return _run_harness(code)

@function_tool()
async def harness_scroll(context: RunContext, x: int, y: int, dy: int) -> str:
    """
    Scroll the page at the given coordinates by dy amount. 
    Negative dy scrolls down, positive dy scrolls up.
    """
    code = f"""
scroll({x}, {y}, dy={dy})
print("Scrolled by {dy} at ({x}, {y})")
"""
    return _run_harness(code)

@function_tool()
async def harness_execute_js(context: RunContext, javascript_code: str) -> str:
    """
    Execute arbitrary JavaScript on the current page.
    Useful for reading the DOM, finding elements, or extracting text.
    Returns the JSON stringified result of the expression.
    """
    code = f"""
result = js({json.dumps(javascript_code)})
print(json.dumps(result))
"""
    return _run_harness(code)

HARNESS_TOOLS = [
    harness_page_info,
    harness_open_url,
    harness_click,
    harness_type,
    harness_screenshot,
    harness_scroll,
    harness_execute_js
]
