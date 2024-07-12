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
while(True):
    elsapedTime = time() - startTime
    if detector.screenshot is None:
        continue
    detector.annotate_detection_midpoint()
    bot.update_results(detector.results)
    cv.imshow("Detection test",detector.screenshot)

    if detector.results and elsapedTime > 4:
        if detector.results[1]:
            bushCord = detector.results[1][0]
            
            x,y = bot.calculate_tile_xy(bot.lastPlayerCord,bushCord)
            print(x,y)
            start = spawnpoint
            end = (int(start[0]+x),int(start[1]+y))

            print(end)
            paths = pathfinder.find_path(start,end)
            for path in paths:
                print(path)
            break
        
    # press 'q' with the output window focused to exit.
    key = cv.waitKey(1)
    if key == ord('q'):
        wincap.stop()
        detector.stop()
        cv.destroyAllWindows()
        break

cv.destroyAllWindows()

cv.drawMarker(detector.screenshot, bushCord,
                (255,0,0) ,thickness=3,
                markerType= cv.MARKER_CROSS,
                line_type=cv.LINE_AA, markerSize=50)
cv.imshow("Detection test",detector.screenshot)
cv.waitKey(0)


print('Done.')

