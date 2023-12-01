import cv2
import numpy
import numpy as np
import time
from utils.arucoHelper import *
from utils.math import *
from utils.gcode import *
from PIL import Image

image = cv2.imread("test/KalibraceTEST.jpg")
detector = load_detector()

DEBUG = False

Right_top_offs = [0,0] # [-50,25]
Left_top_offs = [0,0] # [20,30]
Left_bottom_offs = [0,0] # [20,0]
Right_bottom_offs = [0,0] # [10,0]

markerCorners, markerIds, rejectedCandidates = detector.detectMarkers(image)
cornerList, midPointList = ArucoPoints(markerCorners, markerIds, image, DEBUG)
json_dict = crop_coords(image, midPointList,cornerList, DEBUG)
json_dict = apply_offset(json_dict, Left_top_offs, Right_top_offs, Left_bottom_offs)

if DEBUG:
    for coords in json_dict.values():
        cv2.circle(image, (coords[0], coords[1]), 5, (255, 190, 0), -1)

x, y = calculate_fourth_point(json_dict, Right_bottom_offs)
lowerright = [int(x), int(y)]

cv2.circle(image, (lowerright[0], lowerright[1]), 5, (100, 255, 0), -1)

image_np = crop_pic(json_dict,lowerright, image)
pic = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
pic = cv2.rotate(pic, cv2.ROTATE_180)
cv2.imshow("Input", pic)

gray = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (5, 5), 0)
ret, thresh = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY)
imagem = cv2.bitwise_not(thresh)
contours, hierarchy = cv2.findContours(image=imagem, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)
image_copy = pic.copy()

cv2.imshow('Tresh', thresh)
cv2.drawContours(image_copy, contours, -1, (255, 255, 0), 2)
cv2.imshow("Contours", image_copy)

if contours:
    x_min, y_min, x_max, y_max = cv2.boundingRect(contours[0])

# Iterate through the contours to update min and max values
for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)
    x_min = min(x_min, x)
    y_min = min(y_min, y)
    x_max = max(x_max, x + w)
    y_max = max(y_max, y + h)

# Print the final min and max values
print("x_min:", x_min)
print("x_max:", x_max)
print("y_min:", y_min)
print("y_max:", y_max)

filtered_contours = [contour for contour in new_contours if cv2.contourArea(contour) > threshold]

cv2.drawContours(image_copy, filtered_contours, -1, (255, 100, 0), 2)
cv2.imshow("Contours filtered", image_copy)

cv2.waitKey(0)
cv2.destroyAllWindows()