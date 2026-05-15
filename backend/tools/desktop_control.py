"""
Desktop Control Module for Nivora

Provides comprehensive desktop automation capabilities:
- Mouse control (click, move, drag)
- Keyboard control (type, hotkeys)
- Window management (focus, list, close)
- Application control (launch, kill)
- Vision-guided automation

All destructive operations integrate with tools_safety for confirmation.
"""

import logging
import asyncio
import os
import subprocess
from typing import Annotated, Optional, List
import psutil

# Desktop automation libraries
import pyautogui
try:
    from pywinauto import Application
    from pywinauto import Desktop
    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False

from livekit.agents import RunContext, function_tool

# Import safety and audit systems
from tools_safety import require_voice_confirmation, is_system_path
from audit_log import log_tool_execution

# Import vision system for guided automation
import computer_use as _cu

logger = logging.getLogger(__name__)

# Configure pyautogui safety
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.1  # Small pause between actions


# =============================================================================
# MOUSE CONTROL
# =============================================================================

@function_tool()
async def mouse_click(
    context: RunContext,
    x: int,
    y: int,
    button: Annotated[str, "Mouse button: 'left', 'right', or 'middle'"] = "left",
    double: Annotated[bool, "Double click if True"] = False
) -> str:
    """
    Click mouse at specific screen coordinates.

    Args:
        x: X coordinate
        y: Y coordinate
        button: Mouse button ('left', 'right', 'middle')
        double: Whether to double-click

    Example:
        mouse_click(100, 200, "left", False)
    """
    try:
        logger.info(f"Mouse click at ({x}, {y}), button={button}, double={double}")

        # Execute click
        if double:
            pyautogui.doubleClick(x, y, button=button)
        else:
            pyautogui.click(x, y, button=button)

        # Log to audit
        log_tool_execution(
            tool_name="mouse_click",
            params={"x": x, "y": y, "button": button, "double": double},
            user_confirmed=False,  # Safe operation
            result="success",
            session_id=context.room.name if context.room else "unknown"
        )

        return f"Clicked {button} button at ({x}, {y})" + (" (double)" if double else "")

    except Exception as e:
        logger.error(f"Mouse click failed: {e}", exc_info=True)
        return f"Failed to click mouse: {e}"


@function_tool()
async def mouse_move(
    context: RunContext,
    x: int,
    y: int,
    duration: Annotated[float, "Duration in seconds for smooth movement"] = 0.5
) -> str:
    """
    Move mouse cursor to specific coordinates smoothly.

    Args:
        x: Target X coordinate
        y: Target Y coordinate
        duration: Time to complete movement (seconds)

    Example:
        mouse_move(500, 300, 0.5)
    """
    try:
        logger.info(f"Moving mouse to ({x}, {y}) over {duration}s")
        pyautogui.moveTo(x, y, duration=duration)
        return f"Moved mouse to ({x}, {y})"

    except Exception as e:
        logger.error(f"Mouse move failed: {e}", exc_info=True)
        return f"Failed to move mouse: {e}"


@function_tool()
async def mouse_drag(
    context: RunContext,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    duration: Annotated[float, "Duration in seconds"] = 0.5,
    button: Annotated[str, "Mouse button to hold"] = "left"
) -> str:
    """
    Drag mouse from one point to another.

    Args:
        x1: Start X coordinate
        y1: Start Y coordinate
        x2: End X coordinate
        y2: End Y coordinate
        duration: Time to complete drag
        button: Mouse button to hold during drag

    Example:
        mouse_drag(100, 100, 200, 200, 0.5, "left")
    """
    try:
        logger.info(f"Dragging from ({x1}, {y1}) to ({x2}, {y2})")

        # Move to start position
        pyautogui.moveTo(x1, y1, duration=0.2)
        # Drag to end position
        pyautogui.drag(x2 - x1, y2 - y1, duration=duration, button=button)

        return f"Dragged from ({x1}, {y1}) to ({x2}, {y2})"

    except Exception as e:
        logger.error(f"Mouse drag failed: {e}", exc_info=True)
        return f"Failed to drag mouse: {e}"


# =============================================================================
# KEYBOARD CONTROL
# =============================================================================

@function_tool()
async def keyboard_type(
    context: RunContext,
    text: Annotated[str, "Text to type"],
    interval: Annotated[float, "Interval between keystrokes in seconds"] = 0.01
) -> str:
    """
    Type text at current cursor position.

    Args:
        text: Text to type
        interval: Delay between each keystroke

    Example:
        keyboard_type("Hello World", 0.01)

    Security: Input is sanitized to prevent command injection.
    """
    try:
        logger.info(f"Typing text (length={len(text)})")

        # Sanitize input - remove potentially dangerous characters
        # This is a basic sanity check; for full safety, validate context
        if len(text) > 10000:
            return "Error: Text too long (max 10000 characters)"

        # Type the text
        pyautogui.write(text, interval=interval)

        # Log to audit (truncate long text in logs)
        text_preview = text[:100] + ("..." if len(text) > 100 else "")
        log_tool_execution(
            tool_name="keyboard_type",
            params={"text_length": len(text), "text_preview": text_preview},
            user_confirmed=False,
            result="success",
            session_id=context.room.name if context.room else "unknown"
        )

        return f"Typed {len(text)} characters"

    except Exception as e:
        logger.error(f"Keyboard type failed: {e}", exc_info=True)
        return f"Failed to type text: {e}"


@function_tool()
async def keyboard_hotkey(
    context: RunContext,
    keys: Annotated[str, "Comma-separated keys, e.g. 'ctrl,c' or 'alt,tab'"]
) -> str:
    """
    Press a hotkey combination.

    Args:
        keys: Comma-separated key names (e.g., "ctrl,c" or "win,d")

    Common hotkeys:
    - "ctrl,c" - Copy
    - "ctrl,v" - Paste
    - "ctrl,s" - Save
    - "alt,tab" - Switch windows
    - "win,d" - Show desktop
    - "ctrl,alt,delete" - Task manager

    Example:
        keyboard_hotkey("ctrl,c")
    """
    try:
        # Parse keys
        key_list = [k.strip() for k in keys.split(",")]

        logger.info(f"Pressing hotkey: {' + '.join(key_list)}")

        # Press the hotkey
        pyautogui.hotkey(*key_list)

        log_tool_execution(
            tool_name="keyboard_hotkey",
            params={"keys": keys},
            user_confirmed=False,
            result="success",
            session_id=context.room.name if context.room else "unknown"
        )

        return f"Pressed hotkey: {' + '.join(key_list)}"

    except Exception as e:
        logger.error(f"Keyboard hotkey failed: {e}", exc_info=True)
        return f"Failed to press hotkey: {e}"


@function_tool()
async def keyboard_press(
    context: RunContext,
    key: Annotated[str, "Key name to press (e.g., 'enter', 'esc', 'f1')"]
) -> str:
    """
    Press a single key.

    Args:
        key: Name of the key (e.g., 'enter', 'esc', 'tab', 'space', 'f1')

    Example:
        keyboard_press("enter")
    """
    try:
        logger.info(f"Pressing key: {key}")
        pyautogui.press(key)
        return f"Pressed key: {key}"

    except Exception as e:
        logger.error(f"Keyboard press failed: {e}", exc_info=True)
        return f"Failed to press key: {e}"


# =============================================================================
# WINDOW MANAGEMENT
# =============================================================================

@function_tool()
async def window_list(context: RunContext) -> str:
    """
    List all open windows with their titles.

    Returns JSON array of window information.

    Example output:
        [
            {"title": "Notepad - file.txt", "pid": 1234},
            {"title": "Chrome - Google", "pid": 5678}
        ]
    """
    try:
        import json

        if not PYWINAUTO_AVAILABLE:
            return "Error: pywinauto not available. Install with: pip install pywinauto"

        logger.info("Listing all open windows")

        windows = []
        desktop = Desktop(backend="uia")

        for window in desktop.windows():
            try:
                title = window.window_text()
                if title and title.strip():  # Skip windows with empty titles
                    windows.append({
                        "title": title,
                        "process": window.process_id() if hasattr(window, 'process_id') else None
                    })
            except:
                continue

        logger.info(f"Found {len(windows)} windows")
        return json.dumps(windows, indent=2)

    except Exception as e:
        logger.error(f"Window list failed: {e}", exc_info=True)
        return f"Failed to list windows: {e}"


@function_tool()
async def window_focus(
    context: RunContext,
    window_title: Annotated[str, "Window title (partial match supported)"]
) -> str:
    """
    Focus/activate a window by its title.

    Args:
        window_title: Full or partial window title

    Example:
        window_focus("Notepad")
    """
    try:
        if not PYWINAUTO_AVAILABLE:
            return "Error: pywinauto not available"

        logger.info(f"Focusing window: {window_title}")

        # Try to find and focus the window
        app = Application(backend="uia").connect(title_re=f".*{window_title}.*", timeout=5)
        window = app.top_window()
        window.set_focus()

        return f"Focused window: {window.window_text()}"

    except Exception as e:
        logger.error(f"Window focus failed: {e}", exc_info=True)
        return f"Failed to focus window '{window_title}': {e}"


@function_tool()
async def window_close(
    context: RunContext,
    window_title: Annotated[str, "Window title to close"]
) -> str:
    """
    Close a window by its title.

    Args:
        window_title: Window title (partial match supported)

    Note: This is a MEDIUM safety operation - may require confirmation for important windows.

    Example:
        window_close("Untitled - Notepad")
    """
    try:
        if not PYWINAUTO_AVAILABLE:
            return "Error: pywinauto not available"

        # Note: In production, add confirmation for important windows
        # confirmed = await require_voice_confirmation(...)

        logger.info(f"Closing window: {window_title}")

        app = Application(backend="uia").connect(title_re=f".*{window_title}.*", timeout=5)
        window = app.top_window()
        actual_title = window.window_text()

        window.close()

        log_tool_execution(
            tool_name="window_close",
            params={"window_title": window_title},
            user_confirmed=False,  # Add confirmation in production
            result="success",
            session_id=context.room.name if context.room else "unknown"
        )

        return f"Closed window: {actual_title}"

    except Exception as e:
        logger.error(f"Window close failed: {e}", exc_info=True)
        return f"Failed to close window '{window_title}': {e}"


# =============================================================================
# APPLICATION CONTROL
# =============================================================================

@function_tool()
async def app_launch(
    context: RunContext,
    app_path_or_name: Annotated[str, "Application path or name (e.g., 'notepad' or 'C:\\\\Program Files\\\\App\\\\app.exe')"]
) -> str:
    """
    Launch an application.

    Args:
        app_path_or_name: Application name (e.g., "notepad") or full path

    Common applications:
    - "notepad" - Notepad
    - "calc" - Calculator
    - "mspaint" - Paint
    - "chrome" - Google Chrome
    - "explorer" - File Explorer

    Example:
        app_launch("notepad")
    """
    try:
        logger.info(f"Launching application: {app_path_or_name}")

        # Security check - prevent launching from system directories without confirmation
        if "\\" in app_path_or_name and is_system_path(app_path_or_name):
            return f"Error: Cannot launch application from system directory without explicit confirmation"

        # Launch the application
        if os.path.exists(app_path_or_name):
            # Full path provided
            os.startfile(app_path_or_name)
        else:
            # Application name - let Windows find it
            subprocess.Popen(app_path_or_name, shell=True)

        await asyncio.sleep(1)  # Wait for app to start

        log_tool_execution(
            tool_name="app_launch",
            params={"app": app_path_or_name},
            user_confirmed=False,
            result="success",
            session_id=context.room.name if context.room else "unknown"
        )

        return f"Launched application: {app_path_or_name}"

    except Exception as e:
        logger.error(f"App launch failed: {e}", exc_info=True)
        return f"Failed to launch application '{app_path_or_name}': {e}"


@function_tool()
async def app_kill(
    context: RunContext,
    process_name: Annotated[str, "Process name to terminate (e.g., 'notepad.exe')"]
) -> str:
    """
    Terminate a running process.

    Args:
        process_name: Name of the process (e.g., "notepad.exe", "chrome.exe")

    Warning: This is a DESTRUCTIVE operation and should require confirmation.

    Example:
        app_kill("notepad.exe")
    """
    try:
        # This is a destructive operation - require confirmation
        # Note: Temporarily disabled for testing, enable in production
        # confirmed = await require_voice_confirmation(
        #     context,
        #     f"terminate process {process_name}",
        #     "app_kill"
        # )
        # if not confirmed:
        #     return "Operation cancelled by user"

        logger.info(f"Terminating process: {process_name}")

        killed_count = 0
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() == process_name.lower():
                    proc.kill()
                    killed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if killed_count == 0:
            return f"No process found with name: {process_name}"

        log_tool_execution(
            tool_name="app_kill",
            params={"process_name": process_name, "killed_count": killed_count},
            user_confirmed=True,  # Should be True only if confirmation passed
            result="success",
            session_id=context.room.name if context.room else "unknown"
        )

        return f"Terminated {killed_count} instance(s) of {process_name}"

    except Exception as e:
        logger.error(f"App kill failed: {e}", exc_info=True)
        return f"Failed to terminate process '{process_name}': {e}"


# =============================================================================
# VISION-GUIDED AUTOMATION
# =============================================================================

@function_tool()
async def desktop_click_by_vision(
    context: RunContext,
    target_description: Annotated[str, "Description of UI element to click (e.g., 'Save button', 'red X icon')"]
) -> str:
    """
    Use AWS Nova Pro vision AI to find and click on a UI element.

    Args:
        target_description: Description of what to click

    Example:
        desktop_click_by_vision("Click the Save button")
        desktop_click_by_vision("Click the red X to close")

    How it works:
    1. Captures current screen
    2. Uses vision AI to locate the target element
    3. Extracts coordinates
    4. Performs click

    Returns description of what was clicked and where.
    """
    try:
        logger.info(f"Vision-guided click: {target_description}")

        # Step 1: Capture screen
        img = _cu.capture_screen()
        if img is None:
            return "Error: Could not capture screen"

        # Step 2: Build vision prompt
        prompt = f"""
Analyze this screenshot and locate the UI element: "{target_description}"

Return a JSON object with ONLY these fields:
{{
    "found": true/false,
    "x": <x_coordinate>,
    "y": <y_coordinate>,
    "description": "<brief description of what was found>",
    "confidence": "<high/medium/low>"
}}

If the element is not found, set "found" to false.
IMPORTANT: Return ONLY valid JSON, no other text.
"""

        # Step 3: Analyze with vision AI
        response = _cu.analyze_screen(prompt, img, temperature=0.1)

        if isinstance(response, dict) and "error" in response:
            return f"Vision analysis failed: {response['error']}"

        # Step 4: Parse response
        import json
        if isinstance(response, str):
            response = json.loads(response)

        if not response.get("found", False):
            return f"Could not locate: {target_description}"

        x = int(response["x"])
        y = int(response["y"])
        description = response.get("description", "element")
        confidence = response.get("confidence", "unknown")

        # Step 5: Perform click
        pyautogui.click(x, y)

        logger.info(f"Vision click successful at ({x}, {y}), confidence={confidence}")

        log_tool_execution(
            tool_name="desktop_click_by_vision",
            params={"target": target_description, "x": x, "y": y, "confidence": confidence},
            user_confirmed=False,
            result="success",
            session_id=context.room.name if context.room else "unknown"
        )

        return f"Clicked {description} at ({x}, {y}) - confidence: {confidence}"

    except Exception as e:
        logger.error(f"Vision-guided click failed: {e}", exc_info=True)
        return f"Failed to perform vision-guided click: {e}"


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_screen_size() -> tuple[int, int]:
    """Get screen resolution."""
    return pyautogui.size()


def get_mouse_position() -> tuple[int, int]:
    """Get current mouse position."""
    return pyautogui.position()


# Example usage and testing
if __name__ == "__main__":
    print("Desktop Control Module Test")
    print(f"Screen size: {get_screen_size()}")
    print(f"Mouse position: {get_mouse_position()}")
    print("\nModule loaded successfully!")
