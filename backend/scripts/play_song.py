import urllib.request
import urllib.parse
import re
import webbrowser
import time
import pyautogui

pyautogui.FAILSAFE = False

def play_song(song_name):
    print(f"Searching YouTube directly for '{song_name}'...")
    query = urllib.parse.quote(song_name)
    url = f"https://www.youtube.com/results?search_query={query}"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        
        video_ids = []
        for match in re.finditer(r"watch\?v=([a-zA-Z0-9_-]{11})", html):
            vid = match.group(1)
            if vid not in video_ids:
                video_ids.append(vid)
        
        if video_ids:
            video_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
            print(f"Success! Found direct video URL: {video_url}")
            
            webbrowser.open(video_url)
            
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
    play_song("mutta kalaki song")
