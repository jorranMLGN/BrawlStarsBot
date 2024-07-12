import pyautogui
from time import sleep
from modules.windowcapture import WindowCapture
from modules.screendetect import Screendetect
import keyboard

find_colour = 0
wincap = WindowCapture("Bluestacks App Player")
windowSize = wincap.get_dimension()
screendetect = Screendetect(windowSize,(wincap.offset_x,wincap.offset_y))

if find_colour:
    print("Press q to get scale factor and RGB value\n")
    count = 1
    while True:
        if keyboard.is_pressed('q'):
            x,y = pyautogui.position()
            print(count)
            print("xScaleFactor: ",round((x-wincap.offset_x)/wincap.w,4))
            print("yScaleFactor: ",round((y-wincap.offset_y)/wincap.h,4))
            print("RGB: ",pyautogui.pixel(x,y))
            print("")
            count+=1
            sleep(0.5)
# testing
else:
    while True:
        print(screendetect.is_load_in())
        sleep(0.5)
        

