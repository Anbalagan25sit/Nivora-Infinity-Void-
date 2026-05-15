import webbrowser
import time
import pyautogui

def test():
    # Attempting to load Tamil Gaming latest VOD again
    webbrowser.open("https://www.youtube.com/watch?v=0zpGbecfawg&autoplay=1")
    time.sleep(5)
    
    print("Clicking top left to focus...")
    pyautogui.click(100, 100)
    time.sleep(1)
    
    print("Double clicking center of screen to force interaction...")
    w, h = pyautogui.size()
    pyautogui.doubleClick(w // 2, h // 2 + 50)
    
    time.sleep(0.5)
    print("Pressing 'k' to ensure playback...")
    pyautogui.press('k')

if __name__ == "__main__":
    test()
