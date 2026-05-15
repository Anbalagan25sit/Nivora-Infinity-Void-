import webbrowser
import time
import pyautogui

def reliable_play():
    print("Opening YouTube Search for 'mr ig ets2 latest video'...")
    webbrowser.open('https://www.youtube.com/results?search_query=mr+ig+ets2+latest+video')
    
    # Wait for the page to load completely
    print("Waiting 6 seconds for page load...")
    time.sleep(6)
    
    print("Moving mouse to the center of the first video thumbnail (approx x=600, y=350) and clicking...")
    # These coordinates are typical for a 1080p screen where the first video thumbnail is located
    pyautogui.click(600, 350)
    time.sleep(1)
    pyautogui.click(600, 350) # Double click just in case
    
    print("Also trying the keyboard fallback...")
    pyautogui.press('tab', presses=4, interval=0.1)
    pyautogui.press('enter')
    
    # Let's also press 'k' or space after a moment to ensure it plays
    time.sleep(3)
    pyautogui.press('k')

if __name__ == "__main__":
    reliable_play()
