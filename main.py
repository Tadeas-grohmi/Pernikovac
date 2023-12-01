#Made by Tadeas-grohmi with love <3
import cv2
import numpy
import numpy as np
import time
from utils.arucoHelper import *
from utils.math import *
from utils.gcode import *
from PIL import Image


DEBUG = False

image = cv2.imread("test/main.png")
detector = load_detector()

Right_top_offs = [0,0] # [-50,25]
Left_top_offs = [0,0] # [20,30]
Left_bottom_offs = [0,0] # [20,0]
Right_bottom_offs = [0,0] # [10,0]


def detect_object(image, detector):

    markerCorners, markerIds, rejectedCandidates = detector.detectMarkers(image)
    cornerList, midPointList = ArucoPoints(markerCorners, markerIds, image, DEBUG)
    json_dict = crop_coords(image, midPointList,cornerList, DEBUG)
    json_dict = apply_offset(json_dict, Left_top_offs, Right_top_offs, Left_bottom_offs)

    print(json_dict)

    if DEBUG:
        for coords in json_dict.values():
            cv2.circle(image, (coords[0], coords[1]), 3, (255, 190, 0), -1)

    x, y = calculate_fourth_point(json_dict, Right_bottom_offs)
    lowerright = [int(x), int(y)]

    cv2.circle(image, (lowerright[0], lowerright[1]), 3, (100, 255, 0), -1)

    image_np = crop_pic(json_dict,lowerright, image)

    contours, pic, image_copy = get_contours(image_np, DEBUG)

    con_to_gcode(contours, image_copy, json_dict)


    if DEBUG:
        cv2.imshow('Cropped', pic)
        cv2.imshow('Contours', image_copy)
        cv2.imshow("Detected Markers", image)

detect_object(image, detector)


cv2.waitKey(0)
cv2.destroyAllWindows()