import urllib.request
import urllib.parse
import re
import webbrowser
import time
import pyautogui

def test_tamil():
    query = urllib.parse.quote("tamil gaming live stream")
    url = f"https://www.youtube.com/results?search_query={query}&sp=CAISAhAB"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    html = urllib.request.urlopen(req).read().decode('utf-8')
    
    video_ids = []
    for match in re.finditer(r"watch\?v=([a-zA-Z0-9_-]{11})", html):
        vid = match.group(1)
        if vid not in video_ids:
            video_ids.append(vid)
            
    if video_ids:
        video_url = f"https://www.youtube.com/watch?v={video_ids[0]}&autoplay=1"
        print(f"Found VOD: {video_url}")
        webbrowser.open(video_url)
        time.sleep(5)
        pyautogui.click(100, 100)
    else:
        print("Couldn't find video ID.")

if __name__ == "__main__":
    test_tamil()
