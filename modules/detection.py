from threading import Thread, Lock
from time import time
import cv2 as cv
from settings import Settings
from ultralytics import YOLO
import numpy as np

class Detection:
    # threading properties
    stopped = True
    lock = None

    # properties
    screenshot = None
    results = None
    height = None
    fps = 0
    avg_fps = 0
    player_topleft = None
    player_bottomright = None
    midpoint_offset = Settings.midpointOffsetScale



    red = (0,0,255)

    def __init__(self, wincap, model_file_path, classes):
        """
        Constructor for the Detection class
        """
        # create a thread lock object
        self.lock = Lock()
        # load the trained model
        self.model = YOLO(model_file_path,task="detect")
        if Settings.nvidia_gpu:
            self.model.cuda()
        self.classes = classes
        self.wincap = wincap
        self.windowSize = wincap.get_dimension()
        self.w = self.windowSize[0]
        self.h = self.windowSize[1]
        self.window_center = wincap.get_brawler_center()
    
        if Settings.heightScale:
            self.heightScale = Settings.heightScale
        else:
            self.heightScale = 0.15 # default hsf
        self.height = self.h * self.heightScale
        self.areaThreshold = int(2**2*self.wincap.tilePerWidth*self.wincap.tilePerHeight)
        self.windowScaleFactor = 1

    # The find_midpoint function finds the midpoint of the bounding box of the detection
    # x2 > x1, y2 > y1
    def xyxy_to_xywh(self,x1,y1,x2,y2):
        return x1+int((x2-x1)/2),y1+int((y2-y1)/2),x2-x1,y2-y1

    def predict(self,screenshot):
        return self.model.predict(screenshot, imgsz=Settings.imgsz,
                                        half=Settings.half, verbose=False)
        
    def caculate_heightScale(self):
        results = self.predict(self.screenshot)
        result = results[0]
        for box in result.boxes:
            x1, y1, x2, y2 = [round(x) for x in box.xyxy[0].tolist()]
            class_id = int(box.cls[0].item())
            prob = round(box.conf[0].item(), 2)
            threshold = Settings.threshold[class_id]
            if prob >= threshold:
                midpoint = self.xyxy_to_xywh(x1,y1,x2,y2)
                if self.classes[class_id] == "Player":
                    return abs(midpoint[1] - self.window_center[1]) / self.h


    def annotate_detection_midpoint(self):
        """
        annotate detection
        """
        thickness = 1

        if self.results:
            for i in range(len(self.results)):
                    #if the list is not empty
                    if self.results[i]:
                        for count, cord in enumerate(self.results[i]):
                            color = (0, 0, 255) # bgr
                            if count == 0 and i ==1:
                                color = (0,255,0)
                            cv.drawMarker(self.screenshot, cord,
                                           color ,thickness=thickness,
                                           markerType= cv.MARKER_CROSS,
                                           line_type=cv.LINE_AA, markerSize=50)
                            cv.putText(self.screenshot, self.classes[i],
                                       cord, cv.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    def annotate_border(self,border_size,tile_w,tile_h):
        """
        annotate border for debuggin purposes
        """
        thickness = 2
        # bgr
        green = (0, 255, 0)
        x_scale = int(self.w/3)
        y_scale = int(self.h/3)
        xBorder = (self.w/tile_w)
        yBorder = (self.h/tile_h)
        size = 2*border_size
        xTop = int(xBorder*((tile_w-size)/2))
        yTop = int(yBorder*((tile_h-size)/2))+self.midpoint_offset
        xBottom = int(xBorder*((tile_w+size)/2))
        yBottom = int(yBorder*((tile_h+size)/2))+self.midpoint_offset
        
        cv.rectangle(self.screenshot, (xTop, yTop), (xBottom, yBottom), (0,255,0), 2)
        cv.drawMarker(self.screenshot,self.window_center,
                    green ,thickness=thickness,markerType= cv.MARKER_CROSS,
                    line_type=cv.LINE_AA, markerSize=50)
        #quadrant line
        cv.line(self.screenshot,(x_scale,0),(x_scale,3*y_scale),green,thickness)
        cv.line(self.screenshot,(2*x_scale,0),(2*x_scale,3*y_scale),green,thickness)
        cv.line(self.screenshot,(0,y_scale),(3*x_scale,y_scale),green,thickness)
        cv.line(self.screenshot,(0,2*y_scale),(3*x_scale,2*y_scale),green,thickness)
     
    def annotate_fps(self,wincap_avg_fps):
        scale = (self.windowSize[0]+self.windowSize[1])/(1145+644)
        # make a black solid rectangle at the bottom left corner
        rect_w = int(180*scale)
        rect_h = int(60*scale)
        cv.rectangle(self.screenshot,(0,self.windowSize[1]),
                        (rect_w, self.windowSize[1] - rect_h), (0, 0, 0), -1)
        # FPS text
        fontScale = 0.7*scale
        spacing = int(10*scale)
        thickness = 1
        cv.putText(self.screenshot,text=f"Detect: {int(self.avg_fps)}",
                    org=(0+spacing,self.windowSize[1]-spacing-int(30*scale)),fontFace=cv.FONT_HERSHEY_SIMPLEX,fontScale=fontScale,
                    color=(255,255,255),thickness=thickness)
        cv.putText(self.screenshot,text=f"FPS",
                    org=(0+spacing+int(scale*140),self.windowSize[1]-spacing-int(30*scale)),fontFace=cv.FONT_HERSHEY_SIMPLEX,fontScale=0.5*fontScale,
                    color=(255,255,255),thickness=thickness)
        cv.putText(self.screenshot,text=f"Wincap: {int(wincap_avg_fps)}",
                    org=(0+spacing,self.windowSize[1]-spacing),fontFace=cv.FONT_HERSHEY_SIMPLEX,fontScale=fontScale,
                    color=(255,255,255),thickness=thickness)
        cv.putText(self.screenshot,text=f"FPS",
                    org=(0+spacing+int(scale*140),self.windowSize[1]-spacing),fontFace=cv.FONT_HERSHEY_SIMPLEX,fontScale=0.5*fontScale,
                    color=(255,255,255),thickness=thickness)
        
    def update(self, screenshot):
        self.lock.acquire()
        self.screenshot = screenshot
        self.lock.release()

    def start(self):
        self.stopped = False
        self.loop_time = time()
        self.count = 0
        t = Thread(target=self.run)
        t.setDaemon(True)
        t.start()

    def stop(self):
        self.stopped = True

    def run(self):
        while not self.stopped:
            self.screenshot = self.wincap.get_screenshot()
            if not self.screenshot is None:
                # create empty nested list e.g. [[(..., ...),(..., ...)],[(..., ...)],[(..., ...)],[(..., ...)]]
                tempList = len(self.classes)*[[]] #np.array(len(self.classes)*[[]])
                scaleScreenshot = cv.resize(self.screenshot,(self.wincap.w//self.windowScaleFactor, self.wincap.h//self.windowScaleFactor))
                results = self.predict(scaleScreenshot)
                result = results[0]
                rectangles = []
                largestArea = 0

                for box in result.boxes:
                    prob = round(box.conf[0].item(), 2)
                    class_id = int(box.cls[0].item())
                    threshold = Settings.threshold[class_id]

                    if prob >= threshold:
                        x1, y1, x2, y2 = [round(self.windowScaleFactor*x) for x in box.xyxy[0].cuda().tolist()]
                        x, y, w, h = self.xyxy_to_xywh(x1,y1,x2,y2)

                        if self.classes[class_id] == "Player":
                            # Constantly update player name tag position to check if
                            # player is damaged in bot module while in hiding state
                            self.player_topleft = (x1,y1)
                            self.player_bottomright = (x2,y2)
                            y = y + int(self.height)
                        
                        elif self.classes[class_id] == "Enemy":
                            y = y + int(0.05*self.h)
                        
                        elif self.classes[class_id] == "Bush":
                            area = w*h
                            if area < self.areaThreshold:
                                continue # skip bushes
                            if area > largestArea:
                                largestArea = area
                                if tempList[class_id]:
                                    tempList[class_id][0] = (x,y)
                                continue # skip appending to the 
                                
                        tempList[class_id] = tempList[class_id] + [(x,y)]

                        # cv.rectangle(self.screenshot, (x1, y1), (x2, y2), (0,255,0), 2)
                        # cv.putText(self.screenshot, f"{result.names[class_id]}: {prob}", (x1, y1), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
                
                # iou_threshold = 0
                # rectangles = self.merge_boxes(rectangles, iou_threshold)

                # for x1,y1,x2,y2 in rectangles:
                #     x, y, w, h = self.xyxy_to_xywh(x1,y1,x2,y2)                 
                #     tempList[1] = tempList[1] + [(x,y)]
                #     cv.rectangle(self.screenshot, (x1, y1), (x1+w, y1+h), (0,255,0), 2)

                # lock the thread while updating the results
                self.lock.acquire()
                self.results = tempList
                self.lock.release()
                self.fps = (1 / (time() - self.loop_time))
                self.loop_time = time()
                self.count += 1
                if self.count == 1:
                    self.avg_fps = self.fps
                else:
                    self.avg_fps = (self.avg_fps*self.count+self.fps)/(self.count + 1)