import cv2 as cv
from time import time
from modules.windowcapture import WindowCapture
from modules.screendetect import Screendetect
from modules.detection import Detection
from bot import Brawlbot
from settings import Settings
from ultralytics import YOLO
from collections import defaultdict
import numpy as np
import math
from scipy.spatial import distance
from pathfinder import Pathfinder

def int_tuple(tuple):
    return (int(tuple[0]),int(tuple[1]))

def show_map(screenshot,map,spawnpoint,bushCord,windowSize):
    h, w, _ = map.shape
    scale = int(windowSize[1]*0.4 / h)
    map = cv.resize(map,(scale*w,scale*h),interpolation = cv.INTER_NEAREST)
    cv.circle(map, tuple(scale*i for i in spawnpoint), scale, (255,0,0), 2)
    if bushCord:
        cv.circle(map, tuple(scale*i for i in bushCord), scale, (255,0,0), 2)
    screenshot[0:scale*h, 0:scale*w] = map
    return screenshot

pathfinder = Pathfinder("skull_creek.png")

angles = pathfinder.angles
spawnPoints = pathfinder.spawnPoints

model = YOLO(Settings.model_file_path,task="detect")
# initialize the WindowCapture class
wincap = WindowCapture(Settings.window_name)
#get window dimension
w, h =wincap.get_dimension()
screendetect = Screendetect((w,h),(wincap.offset_x,wincap.offset_y))
# initialize bot class
bot = Brawlbot(wincap, Settings.movementSpeed, Settings.attackRange)


#object detection
classes = Settings.classes
loop_time = time()
bgr = (0,255,0)
# Store the track history
track_history = defaultdict(lambda: [])
randomTrackID = None
start = False
findFirst = True
while(True):
    if screendetect.is_load_in():
        start = True
        startTime = time()

    if start:
        elsapedTime = time() - startTime        
        # Run YOLOv8 tracking on the frame, persisting tracks between frames
        results = model.track(wincap.get_screenshot(), persist=True,verbose=False)

        try:
            # Get the boxes and track IDs
            boxes = results[0].boxes.xywh.cpu()
            track_ids = results[0].boxes.id.int().cpu().tolist()
        except AttributeError:
            continue
        
        # Plot the tracks
        for box, track_id in zip(boxes, track_ids):
            # append to track history 
            x, y, w, h = box
            track = track_history[track_id]
            track.append((float(x), float(y))) 

        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        # Display the annotated frame
        cv.imshow("YOLOv8 Tracking", annotated_frame)

        if elsapedTime > 5:
            break

        # Break the loop if 'q' is pressed
        if cv.waitKey(1) & 0xFF == ord("q"):
            break

# Release the video capture object and close the display window
cv.destroyAllWindows()

longestDistance = 0
for trackId, positions in track_history.items():
    dst = distance.euclidean(positions[0],positions[-1])
    if dst > longestDistance:
        longestDistance = dst
        longestTrackId = trackId
    
myAngle = pathfinder.find_angle(track_history[longestTrackId][-1],track_history[longestTrackId][0])
if myAngle:
    differenceInAngle = [abs(myAngle - angle) for angle in angles]
    # print(f"Angle: {myAngle}")
    # print(differenceInAngle)

    #find the min of the diferences
    minIndex = np.argmin(np.array(differenceInAngle))
    spawnpoint = spawnPoints[minIndex]
    print(f"Spawn-point: {spawnpoint}")
else:
    print("Angle not found!")

detector = Detection(wincap,Settings.model_file_path,Settings.classes)
detector.start()
startTime = time()

end = None
mapImg = cv.imread("skull_creek.png",1)
while(True):
    elsapedTime = time() - startTime
    if detector.screenshot is None:
        continue
    detector.annotate_detection_midpoint()
    bot.update_results(detector.results)
    img = show_map(detector.screenshot,mapImg,spawnpoint,end,wincap.get_dimension())
    cv.imshow("Detection test",img)

    if detector.results and elsapedTime > 4:
        if detector.results[1]:
            bushCord = detector.results[1][0]
            
            x,y = bot.calculate_tile_xy(bot.lastPlayerCord,bushCord)
            x = round(x)
            y = round(y)
            start = spawnpoint
            end = (int(start[0]+x),int(start[1]+y))
            # paths = pathfinder.find_path(start,end)
            # for path in paths:
            #     print(f"{path.x} {path.y}")
        
    # press 'q' with the output window focused to exit.
    key = cv.waitKey(1)
    if key == ord('q'):
        wincap.stop()
        detector.stop()
        cv.destroyAllWindows()
        break

cv.destroyAllWindows()
print('Done.')

