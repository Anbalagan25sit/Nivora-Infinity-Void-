import urllib.request
import urllib.parse
import re
import webbrowser
import time
import pyautogui

pyautogui.FAILSAFE = False

def play_latest():
    print("Searching YouTube for the absolute latest Mr IG ETS2 video/stream...")
    query = urllib.parse.quote("mr ig ets2")
    
    # sp=CAI%3D sorts the search results by Upload Date (newest first)
    url = f"https://www.youtube.com/results?search_query={query}&sp=CAI%253D"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        
        # Extract video IDs
        video_ids = re.findall(r"watch\?v=(\S{11})", html)
        
        if video_ids:
            # First one is the most recently uploaded matching the query
            latest_video_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
            print(f"Success! Found the latest video URL: {latest_video_url}")
            
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
    play_latest()
