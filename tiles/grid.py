import cv2 as cv
from time import sleep
from modules.windowcapture import WindowCapture
from modules.detection import Detection
from settings import Settings


# def draw_grid(screenshot,windowSize,windowMiddle,van,color=(0,255,0),thickness=2):
#     tileScaleX = 0.0432
#     tileScaleY = 0.0575

#     cv.drawMarker(screenshot,windowMiddle,
#             color ,thickness=thickness,markerType= cv.MARKER_CROSS,
#             line_type=cv.LINE_AA, markerSize=30)
    
#     # x vanishing point lines
#     # van = - int(4.73*windowSize[1])
#     x1 = windowMiddle[0]
#     for i in range(14):
#         if i == 0:
#             x1 -= int(0.5*tileScaleX*windowSize[0])
#         else:
#             x1 -= int(tileScaleX*windowSize[0])
#         cv.line(screenshot,(int(windowMiddle[0]),van),(x1,windowSize[1]),color,thickness)

#     x1 = windowMiddle[0]
#     for i in range(14):
#         if i == 0:
#             x1 += int(0.5*tileScaleX*windowSize[0])
#         else:
#             x1 += int(tileScaleX*windowSize[0])
#         cv.line(screenshot,(int(windowMiddle[0]),van),(x1,windowSize[1]),color,thickness)

#     # x  lines
#     x1 = windowMiddle[0]
#     for i in range(14):
#         if i == 0:
#             x1 -= int(0.5*tileScaleX*windowSize[0])
#         else:
#             x1 -= int(tileScaleX*windowSize[0])
#         cv.line(screenshot,(x1,0),(x1,windowSize[1]),(255,0,0),thickness)

#     x1 = windowMiddle[0]
#     for i in range(14):
#         if i == 0:
#             x1 += int(0.5*tileScaleX*windowSize[0])
#         else:
#             x1 += int(tileScaleX*windowSize[0])
#         cv.line(screenshot,(x1,0),(x1,windowSize[1]),(255,0,0),thickness)

    
#     # # y lines
#     # y1 = windowMiddle[1]
#     # for i in range(9):
#     #     if i == 0:
#     #         y1 -= int(0.5*tileScaleY*windowSize[1])
#     #     else:
#     #         y1 -= int(tileScaleY*windowSize[1])
#     #     cv.line(screenshot,(0,y1),(windowSize[0],y1),color,thickness)

#     # y1 = windowMiddle[1]
#     # for i in range(9):
#     #     if i == 0:
#     #         y1 += int(0.5*tileScaleY*windowSize[1])
#     #     else:
#     #         y1 += int(tileScaleY*windowSize[1])
#     #     cv.line(screenshot,(0,y1),(windowSize[0],y1),color,thickness)
#     return screenshot

def draw_grid(screenshot,windowSize,windowMiddle,van,color=(0,255,0),thickness=2):
    tileScaleX = 0.0388
    x1 = windowMiddle[0]
    for i in range(14):
        if i == 0:
            x1 -= int(0.5*tileScaleX*windowSize[0])
        else:
            x1 -= int(tileScaleX*windowSize[0])
        cv.line(screenshot,(int(windowMiddle[0]),van),(x1,341),color,thickness)

    x1 = windowMiddle[0]
    for i in range(14):
        if i == 0:
            x1 += int(0.5*tileScaleX*windowSize[0])
        else:
            x1 += int(tileScaleX*windowSize[0])
        cv.line(screenshot,(int(windowMiddle[0]),van),(x1,341),color,thickness)

   
while True:
    for i in range (-5000,5000,50):
        print(i)
        screenshot = cv.imread("medium.png", cv.IMREAD_COLOR)
        windowSize = (screenshot.shape[1],screenshot.shape[0])
        windowMiddle = (int(windowSize[0]/2),int(windowSize[1]/2+Settings.midpointOffsetScale+(0.0575/5)*screenshot.shape[0]))        
        gridScreenshot = draw_grid(screenshot,windowSize,windowMiddle,i)
        cv.imshow("test",screenshot)
        # waitKey() waits for a key press to close the window and 0 specifies indefinite loop
        cv.waitKey(0)
    
    for i in range (5000,-5000,-50):
        print(i)
        screenshot = cv.imread("medium.png", cv.IMREAD_COLOR)
        windowSize = (screenshot.shape[1],screenshot.shape[0])
        windowMiddle = (int(windowSize[0]/2),int(windowSize[1]/2+Settings.midpointOffsetScale+(0.0575/5)*screenshot.shape[0]))        
        gridScreenshot = draw_grid(screenshot,windowSize,windowMiddle,i)
        cv.imshow("test",screenshot)
        # waitKey() waits for a key press to close the window and 0 specifies indefinite loop
        cv.waitKey(0)

# cv2.destroyAllWindows() simply destroys all the windows we created.
cv.destroyAllWindows()