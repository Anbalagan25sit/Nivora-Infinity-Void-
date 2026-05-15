"""
test_spotify.py — Tests all Spotify browse/info tools using Client Credentials
(NO user login or refresh token required — only CLIENT_ID + CLIENT_SECRET).
Run:  python test_spotify.py
"""
import sys, os, requests
from pathlib import Path
from dotenv import load_dotenv

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=True)

CLIENT_ID     = os.getenv("SPOTIFY_CLIENT_ID", "").strip()
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "").strip()
API_BASE      = "https://api.spotify.com/v1"
SEP = "=" * 60

print(SEP)
print("  FRIDAY JARVIS - Spotify Tool Test (Client Credentials)")
print(SEP)
print(f"  Client ID     : {'OK' if CLIENT_ID else 'NOT SET'}")
print(f"  Client Secret : {'OK' if CLIENT_SECRET else 'NOT SET'}")
print(SEP)

if not CLIENT_ID or not CLIENT_SECRET:
    print("  ERROR: Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env")
    sys.exit(1)

# ── Get token via Client Credentials ─────────────────────────
def get_token():
    r = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(CLIENT_ID, CLIENT_SECRET),
        timeout=10,
    )
    r.raise_for_status()
    return r.json().get("access_token")

def api(path, params=None):
    r = requests.get(API_BASE + path, headers={"Authorization": f"Bearer {TOKEN}"},
                     params=params or {}, timeout=10)
    if r.status_code == 204:
        return {}
    r.raise_for_status()
    return r.json()

print("\n[0] Getting Client Credentials token ...")
try:
    TOKEN = get_token()
    print(f"  [OK] Token: {TOKEN[:30]}...")
except Exception as e:
    print(f"  [FAIL] {e}")
    sys.exit(1)

# ── 1. Search ─────────────────────────────────────────────────
print("\n[1/7] spotify_search — 'AR Rahman' (track) ...")
try:
    data = api("/search", {"q": "AR Rahman", "type": "track", "limit": 3})
    for t in (data.get("tracks") or {}).get("items") or []:
        print(f"  - {t['name']} by {', '.join(a['name'] for a in t['artists'])}")
    print("  [OK]")
except Exception as e:
    print(f"  [FAIL] {e}")

# ── 2. Track Info ─────────────────────────────────────────────
print("\n[2/7] spotify_get_track_info — 'Vande Mataram (AR Rahman)' ...")
try:
    # Search first to get an ID
    data = api("/search", {"q": "Vande Mataram AR Rahman", "type": "track", "limit": 1})
    items = (data.get("tracks") or {}).get("items") or []
    if items:
        tid = items[0]["id"]
        t = api(f"/tracks/{tid}")
        dur = f"{t['duration_ms']//60000}:{(t['duration_ms']%60000)//1000:02d}"
        print(f"  Track: {t['name']}")
        print(f"  Album: {t['album']['name']}")
        print(f"  Duration: {dur} | Popularity: {t['popularity']}/100")
        print("  [OK]")
    else:
        print("  [SKIP] No track found")
except Exception as e:
    print(f"  [FAIL] {e}")

# ── 3. Artist Info ────────────────────────────────────────────
print("\n[3/7] spotify_get_artist_info — 'Arijit Singh' ...")
try:
    data = api("/search", {"q": "Arijit Singh", "type": "artist", "limit": 1})
    items = (data.get("artists") or {}).get("items") or []
    if items:
        a = items[0]
        print(f"  Artist: {a['name']}")
        print(f"  Genres: {', '.join(a.get('genres',[]) or ['N/A'])}")
        print(f"  Followers: {a['followers']['total']:,} | Popularity: {a['popularity']}/100")
        print("  [OK]")
except Exception as e:
    print(f"  [FAIL] {e}")

# ── 4. Artist Top Tracks ──────────────────────────────────────
print("\n[4/7] spotify_get_artist_top_tracks — 'Arijit Singh' ...")
try:
    data = api("/search", {"q": "Arijit Singh", "type": "artist", "limit": 1})
    aid = ((data.get("artists") or {}).get("items") or [{}])[0].get("id")
    if aid:
        tops = api(f"/artists/{aid}/top-tracks", {"market": "US"})
        for i, t in enumerate((tops.get("tracks") or [])[:5], 1):
            print(f"  {i}. {t['name']} (pop: {t['popularity']})")
        print("  [OK]")
except Exception as e:
    print(f"  [FAIL] {e}")

# ── 5. New Releases ───────────────────────────────────────────
print("\n[5/7] spotify_get_new_releases (limit=5) ...")
try:
    data = api("/browse/new-releases", {"limit": 5})
    for a in (data.get("albums") or {}).get("items") or []:
        print(f"  - {a['name']} by {', '.join(ar['name'] for ar in a['artists'])}")
    print("  [OK]")
except Exception as e:
    print(f"  [FAIL] {e}")

# ── 6. Categories ─────────────────────────────────────────────
print("\n[6/7] spotify_get_categories (limit=8) ...")
try:
    data = api("/browse/categories", {"limit": 8, "locale": "en_US"})
    for c in (data.get("categories") or {}).get("items") or []:
        print(f"  - {c['name']} (id: {c['id']})")
    print("  [OK]")
except Exception as e:
    print(f"  [FAIL] {e}")

# ── 7. Recommendations ────────────────────────────────────────
print("\n[7/7] spotify_get_recommendations (genre: indian,pop, limit=5) ...")
try:
    data = api("/recommendations", {"seed_genres": "indian,pop", "limit": 5})
    for t in data.get("tracks") or []:
        print(f"  - {t['name']} by {', '.join(a['name'] for a in t['artists'])}")
    print("  [OK]")
except Exception as e:
    print(f"  [FAIL] {e}")

print("\n" + SEP)
print("  All Spotify browse tests complete!")
print(SEP)
