import os
import asyncio
import urllib.parse
import pyautogui

async def force_play_spotify():
    print("Testing Spotify local search and play macro again...")
    query = "mutta kalaki"
    encoded_query = urllib.parse.quote(query)
    
    os.startfile(f"spotify:search:{encoded_query}")
    print("Opened search page, waiting 3 seconds...")
    await asyncio.sleep(3)
    
    print("Clicking near the top to focus, then hitting Enter...")
    # Sometimes just hitting 'enter' after a search directly plays the top result if the search bar is focused!
    pyautogui.press('enter')
    
    # If not, let's tab once
    await asyncio.sleep(1)
    pyautogui.press('tab')
    pyautogui.press('enter')

if __name__ == "__main__":
    asyncio.run(force_play_spotify())
