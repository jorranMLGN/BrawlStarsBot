import numpy as np
import cv2
import math
from settings import Settings

# Read input image
img = cv2.imread("largeV2.png")
hh, ww = img.shape[:2]

# Specify input coordinates for corners of red quadrilateral in order TL, TR, BR, BL as x, y
input_pts = np.float32([[426, 159], [1434, 159], [1521, 1046], [338, 1046]])

# Calculate the width and height of the new perspective
width = round(math.hypot(input_pts[0, 0] - input_pts[1, 0], input_pts[0, 1] - input_pts[1, 1]))
height = round(math.hypot(input_pts[0, 0] - input_pts[3, 0], input_pts[0, 1] - input_pts[3, 1]))
print("width:", width, "height:", height)

# Set the upper left coordinates for the output rectangle
x, y = input_pts[0, 0], input_pts[0, 1]

# Specify output coordinates for corners of red quadrilateral in order TL, TR, BR, BL as x, y
output_pts = np.float32([[x, y], [x + width, y], [x + width, y + height], [x, y + height]])

# Compute the perspective transformation matrix
matrix = cv2.getPerspectiveTransform(input_pts, output_pts)
print(matrix)

# Apply the perspective transformation
imgOutput = cv2.warpPerspective(img, matrix, (ww, hh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))

# Function to transform a coordinate from the input plane to the output plane
def transform_coordinate(matrix, point):
    point_homogeneous = np.array([point[0], point[1], 1.0])
    transformed_point_homogeneous = np.dot(matrix, point_homogeneous)
    transformed_point_homogeneous /= transformed_point_homogeneous[2]
    return int(transformed_point_homogeneous[0]), int(transformed_point_homogeneous[1])

# Example coordinate to transform
input_coord1 = (1308, 251)
output_coord1 = transform_coordinate(matrix, input_coord1)


windowSize = (img.shape[1],img.shape[0])
input_coord2 = (int(windowSize[0]/2),int(windowSize[1]/2+Settings.midpointOffsetScale))
output_coord2 = transform_coordinate(matrix, input_coord2)
cv2.line(img,input_coord1,input_coord2,(0,0,255),3)
cv2.line(imgOutput,output_coord1,output_coord2,(0,0,255),3)
# Draw a circle on the transformed point

cv2.imwrite("output.jpg",imgOutput)
cv2.imshow("before",img)
# Display the result
cv2.imshow("result", imgOutput)
cv2.waitKey(0)
cv2.destroyAllWindows()
