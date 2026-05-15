import webbrowser
import time
import pyautogui

def force_play():
    print("Opening YouTube Search...")
    webbrowser.open('https://www.youtube.com/results?search_query=mr+ig+ets2+latest+video')
    
    # Wait 5 seconds for page load
    print("Waiting 5 seconds for page to load...")
    time.sleep(5)
    
    # Tab to the first video title/thumbnail. The number of tabs varies, but usually 4-8.
    print("Pressing Tab 8 times to reach first video...")
    for _ in range(8):
        pyautogui.press('tab')
        time.sleep(0.1)
    
    print("Pressing Enter to play...")
    pyautogui.press('enter')
    
    print("If it didn't play, we can use an alternative method.")

if __name__ == "__main__":
    force_play()
