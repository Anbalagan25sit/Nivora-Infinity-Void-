import asyncio
import logging
import webbrowser
import time
import pyautogui
from urllib.parse import quote_plus

logging.basicConfig(level=logging.INFO)

def play_first_video(query):
    print(f"Searching and playing first video for: {query}")
    encoded = quote_plus(query)
    url = f"https://www.youtube.com/results?search_query={encoded}"
    webbrowser.open(url)
    
    # Wait for the page to load
    time.sleep(4)
    
    # Tab a few times to get to the first video thumbnail and press enter
    # Typically it's 4-5 tabs from page load, but we can also use a visual macro or just rely on the search URL
    print("Pressing Tab 4 times and Enter to play the first result...")
    pyautogui.press('tab', presses=4, interval=0.2)
    pyautogui.press('enter')
    
    print("Should be playing now!")

if __name__ == "__main__":
    play_first_video("mr ig ets2 latest video")
