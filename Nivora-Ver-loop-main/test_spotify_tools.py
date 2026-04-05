"""
test_spotify_tools.py — Unit tests for spotify_play, spotify_control, open_spotify.
Patches webbrowser and pyautogui so no real browser or keypress needed.
Run:  python test_spotify_tools.py
"""
import sys, os, asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Clear Spotify env vars: is_configured() must return False
for k in ("SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET", "SPOTIFY_REFRESH_TOKEN"):
    os.environ.pop(k, None)

# Inject mocks BEFORE tools.py is imported (it imports pyautogui at module level)
mock_pyag = MagicMock()
mock_wb   = MagicMock()
sys.modules["pyautogui"]        = mock_pyag
sys.modules["pywhatkit"]        = MagicMock()
sys.modules["gspread"]          = MagicMock()
sys.modules["duckduckgo_search"]= MagicMock()
sys.modules["duckduckgo_search.DDGS"] = MagicMock()

sys.path.insert(0, str(Path(__file__).parent))
import tools  # imported with pyautogui mocked

# Patch webbrowser.open INSIDE the tools module (where it's actually called)
import webbrowser as _wb_real
mock_wb = MagicMock()
tools.webbrowser.open = mock_wb  # patch in-place after import

SEP = "=" * 62
passed = 0
failed = 0

def ok(name):
    global passed; passed += 1
    print(f"  [OK]   {name}")

def fail(name, reason=""):
    global failed; failed += 1
    print(f"  [FAIL] {name}" + (f"\n         -> {reason}" if reason else ""))

def get_fn(tool):
    """Return the raw async function from a livekit FunctionTool."""
    return tool._func  # livekit wraps with _func

async def run():
    print(SEP)
    print("  Spotify Tools Unit Test (mock browser + pyautogui)")
    print(SEP)

    open_spotify    = get_fn(tools.open_spotify)
    spotify_play    = get_fn(tools.spotify_play)
    spotify_control = get_fn(tools.spotify_control)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # open_spotify URL routing
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n[1] open_spotify — URL routing")
    url_cases = [
        ("home",      {},                               "open.spotify.com",                 None),
        ("search",    {"query": "AR Rahman"},           "open.spotify.com/search/",         None),
        ("track",     {"content_id": "abc123"},         "open.spotify.com/track/abc123",    None),
        ("album",     {"content_id": "abc123"},         "open.spotify.com/album/abc123",    None),
        ("artist",    {"content_id": "abc123"},         "open.spotify.com/artist/abc123",   None),
        ("playlist",  {"content_id": "abc123"},         "open.spotify.com/playlist/abc123", None),
        ("library",   {},                               "collection/tracks",                None),
        ("queue",     {},                               "open.spotify.com/queue",           None),
        ("recent",    {},                               "recently-played",                  None),
    ]
    for mode, kwargs, expected_fragment, _ in url_cases:
        mock_wb.reset_mock()
        await open_spotify(context=None, mode=mode, **kwargs)
        url = mock_wb.call_args[0][0] if mock_wb.called else "(no call)"
        if expected_fragment in url:
            ok(f"mode='{mode}' -> {url}")
        else:
            fail(f"mode='{mode}'", f"expected '{expected_fragment}' in URL, got: {url}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # spotify_play — web player fallback
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n[2] spotify_play — web player fallback (no creds)")

    # With query: must open web search URL + press Tab
    mock_wb.reset_mock(); mock_pyag.reset_mock()
    await spotify_play(context=None, query="Coldplay Yellow")
    url = mock_wb.call_args[0][0] if mock_wb.called else "(no call)"
    all_calls = str(mock_pyag.mock_calls)
    if "open.spotify.com/search/" in url:
        ok(f"opens search URL: {url}")
    else:
        fail("play: search URL", f"got: {url}")
    if "tab" in all_calls.lower():
        ok(f"presses Tab: {all_calls[:80]}")
    else:
        fail("play: Tab key", f"pyautogui calls: {all_calls[:120]}")

    # Without query: must open home + press Space
    mock_wb.reset_mock(); mock_pyag.reset_mock()
    await spotify_play(context=None, query="")
    url = mock_wb.call_args[0][0] if mock_wb.called else "(no call)"
    all_calls = str(mock_pyag.mock_calls)
    if "open.spotify.com" in url:
        ok(f"no-query opens home: {url}")
    else:
        fail("play: home URL", f"got: {url}")
    if "space" in all_calls.lower():
        ok(f"presses Space: {all_calls[:80]}")
    else:
        fail("play: Space key", f"pyautogui calls: {all_calls[:120]}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # spotify_control — keyboard shortcuts
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n[3] spotify_control — keyboard shortcuts")
    shortcut_cases = [
        ("play",        "space"),
        ("pause",       "space"),
        ("next",        "ctrl"),
        ("previous",    "ctrl"),
        ("volume up",   "ctrl"),
        ("volume down", "ctrl"),
        ("mute",        "ctrl"),
        ("shuffle",     "ctrl"),
        ("repeat",      "ctrl"),
        ("like",        "alt"),
        ("search",      "ctrl"),
    ]
    for cmd, expected_key in shortcut_cases:
        mock_pyag.reset_mock()
        result = await spotify_control(context=None, command=cmd)
        all_calls = str(mock_pyag.mock_calls).lower()
        if expected_key in all_calls:
            ok(f"'{cmd}' -> key '{expected_key}' pressed | result: {result}")
        else:
            fail(f"'{cmd}'", f"expected '{expected_key}' in {mock_pyag.mock_calls}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n" + SEP)
    total = passed + failed
    print(f"  Result: {passed}/{total} passed, {failed}/{total} failed")
    if failed == 0:
        print("  All Spotify tool tests PASSED!")
    else:
        print("  Some tests FAILED — see above for details.")
    print(SEP)

asyncio.run(run())
