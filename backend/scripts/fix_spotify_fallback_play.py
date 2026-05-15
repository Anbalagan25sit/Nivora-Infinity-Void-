import os
import asyncio
import urllib.parse
import pyautogui

async def force_play_spotify():
    print("Testing Spotify local search and play macro...")
    query = "mutta kalaki"
    encoded_query = urllib.parse.quote(query)
    
    os.startfile("spotify:")
    await asyncio.sleep(2)
    
    os.startfile(f"spotify:search:{encoded_query}")
    print("Opened search page, waiting 2 seconds...")
    await asyncio.sleep(2)
    
    print("Tabbing 1 time and pressing enter...")
    pyautogui.press('tab', presses=1)
    pyautogui.press('enter')
    
    print("If it didn't play, let's try tabbing twice and enter...")
    await asyncio.sleep(2)
    
    # Try one more time with a slightly different macro
    pyautogui.press('tab', presses=1)
    pyautogui.press('enter')

if __name__ == "__main__":
    asyncio.run(force_play_spotify())
