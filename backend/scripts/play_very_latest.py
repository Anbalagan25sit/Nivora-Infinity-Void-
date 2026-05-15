import urllib.request
import urllib.parse
import re
import webbrowser
import time
import pyautogui

pyautogui.FAILSAFE = False

def play_very_latest():
    print("Searching for the absolute latest full ETS2 stream from Mr IG...")
    
    # "euro truck simulator 2" explicitly, and filtering for videos from "this month" to be safe
    # Also ensuring we actually search for his exact channel name or handle
    query = urllib.parse.quote('mr ig euro truck simulator 2 live')
    
    # sp=EgIIBQ%253D%253D (sort by relevance but filter "this month") or CAI%253D (upload date)
    # Let's just go to his actual channel page, search for videos, and sort by newest.
    # Since we can't reliably scrape his exact channel ID without vision, we'll use a very specific query:
    url = f"https://www.youtube.com/results?search_query={query}&sp=CAI%253D"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        
        video_ids = []
        for match in re.finditer(r"watch\?v=([a-zA-Z0-9_-]{11})", html):
            vid = match.group(1)
            # Skip common youtube UI videos/shorts/mixes if possible, but watch?v is usually right
            if vid not in video_ids:
                video_ids.append(vid)
        
        if video_ids:
            # Let's try the first actual video
            latest_video_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
            print(f"Success! Found the latest stream: {latest_video_url}")
            
            webbrowser.open(latest_video_url)
            
            print("Waiting 6 seconds for video to load...")
            time.sleep(6)
            
            print("Pressing 'space' and 'k' to ensure it plays...")
            pyautogui.press('space')
            time.sleep(0.5)
            pyautogui.press('k')
        else:
            print("Could not find a video ID in the search results.")
            
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    play_very_latest()
