import cv2 as cv
from time import time,sleep
from modules.windowcapture import WindowCapture
from bot import Brawlbot, BotState
from modules.screendetect import Screendetect, Detectstate
from modules.detection import Detection
from modules.print import bcolors
import pyautogui as py
import os
from settings import Settings

# initialize the WindowCapture class
wincap = WindowCapture(Settings.window_name)
# get window dimension
windowSize = wincap.get_dimension()
print(windowSize)
# set target window as foreground
sleep(0.5)
wincap.set_window()

# initialize detection class
detector = Detection(windowSize,Settings.model_file_path,Settings.classes)
# initialize bot class
bot = Brawlbot(wincap, Settings.movementSpeed, Settings.attackRange)

#start thread
wincap.start()
detector.start()
bot.start()

print("start bot")
while True:
    screenshot = wincap.screenshot
    if screenshot is None:
        continue
    # update screenshot for dectector
    detector.update(screenshot)
    bot.update_results(detector.results)

    # font 
    font = cv.FONT_HERSHEY_SIMPLEX 
    
    # org 
    org = wincap.get_window_center() 
    
    # fontScale 
    fontScale = 1
    
    # Blue color in BGR 
    color = (255, 0, 0) 
    
    # Line thickness of 2 px 
    thickness = 2
    if bot.enemyDistance is not None:
        cv.circle(detector.screenshot, bot.lastPlayerCord,int(bot.enemyDistance*(bot.tilePerWidth+bot.tilePerHeight)/2), color, thickness)
    # display annotated window with FPS
    if Settings.DEBUG:
        detector.annotate_detection_midpoint()
        detector.annotate_fps(wincap.avg_fps)
        cv.drawMarker(detector.screenshot, wincap.get_window_center(),
                (0,255,0) ,thickness=thickness,
                markerType= cv.MARKER_CROSS,
                line_type=cv.LINE_AA, markerSize=50)
        cv.imshow("Brawl Stars Bot",detector.screenshot)
    
    # Press q to exit the script
    key = cv.waitKey(1)
    if (key == ord('q')):
        #stop all threads
        detector.stop()
        bot.stop()
        break 