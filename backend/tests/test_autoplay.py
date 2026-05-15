import webbrowser
import time
import pyautogui

def test():
    # Open a video with autoplay
    webbrowser.open("https://www.youtube.com/watch?v=jZEA2mMwL1k&autoplay=1")
    time.sleep(4)
    # Click near the top left (YouTube logo area) just to focus the window, not the video player
    pyautogui.click(100, 100)

if __name__ == "__main__":
    test()
