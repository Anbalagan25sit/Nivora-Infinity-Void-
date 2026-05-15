import asyncio
import pyautogui

async def play():
    # The big green play button on a Spotify Album/Single page
    # It is usually located right below the cover art.
    w, h = pyautogui.size()
    
    print("Clicking the Big Green Play Button...")
    # This coordinate targets the big green play button in the screenshot
    pyautogui.click(w // 2 - 300, h // 2 - 50)

if __name__ == "__main__":
    asyncio.run(play())
