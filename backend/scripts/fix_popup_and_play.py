import webbrowser
import time
import pyautogui

def fix_and_play():
    print("Opening YouTube Search...")
    webbrowser.open('https://www.youtube.com/results?search_query=mr+ig+ets2+latest+video')
    
    # Wait for browser to open and popup to appear
    print("Waiting 4 seconds...")
    time.sleep(4)
    
    print("Pressing 'Escape' multiple times to dismiss the 'Restore Pages' popup...")
    for _ in range(3):
        pyautogui.press('esc')
        time.sleep(0.5)
        
    print("Moving mouse to click the first video...")
    pyautogui.click(600, 350)
    time.sleep(1)
    pyautogui.click(600, 350)
    
    print("Trying keyboard fallback just in case...")
    pyautogui.press('tab', presses=4, interval=0.1)
    pyautogui.press('enter')
    
    print("Pressing 'k' to ensure playback...")
    time.sleep(2)
    pyautogui.press('k')

if __name__ == "__main__":
    fix_and_play()
