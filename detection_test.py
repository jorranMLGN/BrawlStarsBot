import cv2 as cv
from time import sleep
from modules.windowcapture import WindowCapture
from modules.detection import Detection
from settings import Settings
import numpy as np


wincap = WindowCapture(Settings.window_name)
# get window dimension
windowSize = wincap.get_dimension()
# set target window as foreground
sleep(0.5)
wincap.focus_window()

# initialize detection class
detector = Detection(wincap,Settings.model_file_path,Settings.classes)
print(f"w:{wincap.tilePerWidth}, h:{wincap.tilePerHeight}, area: {detector.areaThreshold}")
detector.start()

print(f"Resolution: {wincap.screen_resolution}")
print(f"Window Size: {windowSize}")     
print(f"Scaling: {wincap.scaling*100}%")

while(True):
    # screenshot = wincap.screenshot
    if detector.screenshot is None:
        continue
    # # detector.update(screenshot)
    detector.annotate_detection_midpoint()

    detector.annotate_fps(wincap.avg_fps)
    cv.imshow("Detection test",detector.screenshot)

    # press 'q' with the output window focused to exit.
    key = cv.waitKey(1)
    if key == ord('q'):
        wincap.stop()
        detector.stop()
        cv.destroyAllWindows()
        break
print('Done.')