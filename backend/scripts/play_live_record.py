import urllib.request
import urllib.parse
import re
import webbrowser
import time
import pyautogui

pyautogui.FAILSAFE = False

def play_live_record():
    print("Searching YouTube for past live streams (VODs)...")
    # Added "live stream" to specifically target his recorded streams
    query = urllib.parse.quote("mr ig ets2 live stream")
    
    # sp=EgIYAg%3D%3D filters for videos longer than 20 minutes (which live streams usually are)
    url = f"https://www.youtube.com/results?search_query={query}&sp=EgIYAg%253D%253D"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        
        video_ids = re.findall(r"watch\?v=(\S{11})", html)
        
        if video_ids:
            first_video_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
            print(f"Success! Found direct VOD URL: {first_video_url}")
            
            webbrowser.open(first_video_url)
            
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
    play_live_record()
