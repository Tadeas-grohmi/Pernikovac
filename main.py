import cv2
import numpy
import numpy as np
import time
from utils.arucoHelper import *
from utils.math import *
from PIL import Image


DEBUG = True

image = cv2.imread("test/test3.jpg")
detector = load_detector()



def detect_object(image, detector):

    markerCorners, markerIds, rejectedCandidates = detector.detectMarkers(image)
    cornerList, midPointList = ArucoPoints(markerCorners, markerIds, image, DEBUG)
    json_dict = crop_coords(image, midPointList,cornerList, DEBUG)

    x, y = calculate_fourth_point(json_dict["top_left"][0], json_dict["top_left"][1], json_dict["top_right"][0], json_dict["top_right"][1], json_dict["bottom_left"][0], json_dict["bottom_left"][1])
    lowerright = [int(x), int(y)]

    image_np = crop_pic(json_dict,lowerright, image)

    contours, pic, image_copy = get_contours(image_np, DEBUG)

    if DEBUG:
        cv2.imshow('Cropped', pic)
        cv2.imshow('Contours', image_copy)
        cv2.imshow("Detected Markers", image)

detect_object(image, detector)


cv2.waitKey(0)
cv2.destroyAllWindows()