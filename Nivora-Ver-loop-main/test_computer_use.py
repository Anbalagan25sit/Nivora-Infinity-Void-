"""
test_computer_use.py — Live browser test for the Computer Use engine.
Uses AWS Bedrock Nova Pro to:
  1. Open YouTube in Chrome
  2. Screenshot → analyze → find search bar
  3. Type a search query
  4. Screenshot → analyze → click the best video result
  5. Handle ad if present
  6. Report what's playing

Run:  python test_computer_use.py [query]
Example: python test_computer_use.py "Blinding Lights The Weeknd"
"""
import sys
import os
import time
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Force UTF-8 on Windows
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=_env_path, override=True)

SEP = "=" * 65

print(SEP)
print("  NIVORA — Computer Use Test (AWS Nova Pro + Chrome)")
print(SEP)

# ─── Config ───────────────────────────────────────────────────────────────────
QUERY = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Blinding Lights The Weeknd official"
BACKEND = os.getenv("COMPUTER_USE_BACKEND", "aws")
print(f"  Query  : {QUERY}")
print(f"  Backend: {BACKEND}")
print(SEP)

# ─── Imports ──────────────────────────────────────────────────────────────────
try:
    import computer_use as cu
    print("[OK] computer_use imported")
except ImportError as e:
    print(f"[FAIL] Cannot import computer_use: {e}")
    sys.exit(1)

try:
    from aws_config import bedrock_client, bedrock_model, is_configured
    if not is_configured():
        print("[WARN] AWS credentials not set — AWS backend will fail, check .env")
    else:
        print(f"[OK] AWS configured — model: {bedrock_model()}")
except ImportError as e:
    print(f"[WARN] aws_config import failed: {e}")


# ─── Test Helper ──────────────────────────────────────────────────────────────
def screenshot_and_save(name: str):
    img = cu.capture_screen()
    out = Path(__file__).parent / f"_cu_test_{name}.png"
    img.save(str(out))
    print(f"  Screenshot saved: {out.name}")
    return img


# ─── STEP 1: Open YouTube in Chrome ───────────────────────────────────────────
print("\n[1/5] Opening YouTube in browser...")
import webbrowser, urllib.parse
encoded_query = urllib.parse.quote(QUERY)
search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
webbrowser.open(search_url)
print(f"  Opened: {search_url}")
print("  Waiting 3s for page to load...")
time.sleep(3)

# ─── STEP 2: Screenshot → Analyze screen with AWS Nova ────────────────────────
print(f"\n[2/5] Analyzing YouTube search results page via {BACKEND.upper()} vision...")
img = screenshot_and_save("search_results")

select_prompt = cu.build_youtube_select_prompt(QUERY)
print("  Sending screenshot to vision model...")
t0 = time.time()
selection = cu.analyze_screen(select_prompt, img, backend=BACKEND)
elapsed = time.time() - t0
print(f"  Vision response received in {elapsed:.1f}s")

# Show raw result
if "error" in selection:
    print(f"  [WARN] Vision error: {selection.get('error')}")
    print(f"  Raw: {selection.get('raw', '')[:300]}")
else:
    best = selection.get("best_match", {})
    coords = best.get("coordinates", [])
    title = best.get("title", "?")
    channel = best.get("channel", "?")
    confidence = best.get("confidence", 0)
    reason = best.get("selection_reason", "")
    print(f"  Best match  : '{title}'")
    print(f"  Channel     : {channel}")
    print(f"  Confidence  : {confidence:.0%}")
    print(f"  Coordinates : {coords}")
    print(f"  Reason      : {reason}")

    top3 = selection.get("top_3_results", [])
    if top3:
        print(f"  Top {len(top3)} results also found:")
        for r in top3:
            t_title = r.get("title") or r.get("video_title", "?")
            t_ch = r.get("channel", "?")
            print(f"    - '{t_title}' by {t_ch}")

# ─── STEP 3: Click the best result ────────────────────────────────────────────
if "error" not in selection:
    best = selection.get("best_match", {})
    coords = best.get("coordinates", [])
    if coords and len(coords) >= 2:
        print(f"\n[3/5] Clicking best result at {coords}...")
        cu.execute_action({"action": "click", "coordinates": coords,
                           "description": f"Click: {best.get('title', QUERY)}", "wait_ms": 500})
        print("  Clicked! Waiting 3s for video to load...")
        time.sleep(3)
    else:
        print("\n[3/5] No coordinates returned — skipping click.")
else:
    print("\n[3/5] Skipping click due to vision error.")

# ─── STEP 4: Screenshot → Check for ads ───────────────────────────────────────
print("\n[4/5] Checking for ads...")
img2 = screenshot_and_save("after_click")
ad_info = cu.analyze_screen(cu.PROMPT_YOUTUBE_AD, img2, backend=BACKEND)

if "error" in ad_info:
    print(f"  [WARN] Ad check failed: {ad_info.get('error')}")
elif ad_info.get("ad_detected"):
    ad_type = ad_info.get("ad_type", "?")
    skip_visible = ad_info.get("skip_button_visible", False)
    skip_in = ad_info.get("skip_available_in_seconds", 0)
    print(f"  Ad detected! Type: {ad_type} | Skippable: {skip_visible} | Skip in: {skip_in}s")
    skip_coords = ad_info.get("skip_button_coordinates", [])
    if skip_visible and skip_coords:
        if skip_in > 0:
            print(f"  Waiting {skip_in}s before skipping...")
            time.sleep(skip_in + 0.5)
        cu.execute_action({"action": "click", "coordinates": skip_coords,
                           "description": "Skip ad", "wait_ms": 300})
        print("  Ad skipped!")
    else:
        print(f"  Non-skippable ad — waiting {skip_in}s...")
        time.sleep(max(skip_in, 5))
else:
    print("  No ad detected. Video should be playing.")

# ─── STEP 5: Final screenshot + analyze ───────────────────────────────────────
print("\n[5/5] Final screen analysis...")
time.sleep(1)
img3 = screenshot_and_save("playing")
final = cu.analyze_screen(cu.PROMPT_YOUTUBE_ANALYZE, img3, backend=BACKEND)

if "error" not in final:
    state = final.get("youtube_state", "?")
    video = final.get("current_video", {})
    playing = final.get("is_playing", False)
    print(f"  YouTube state : {state}")
    print(f"  Is playing    : {playing}")
    print(f"  Video title   : {video.get('title', '?')}")
    print(f"  Channel       : {video.get('channel', '?')}")
    print(f"  Current time  : {video.get('current_time', '?')}")
else:
    print(f"  [WARN] Final analysis error: {final.get('error')}")

print("\n" + SEP)
print(f"  Computer Use test complete for: '{QUERY}'")
print(SEP)
