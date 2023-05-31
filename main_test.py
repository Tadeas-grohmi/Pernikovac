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

    try:
        pil_img = Image.fromarray(image)
        img_croped = pil_img.crop((json_dict["top_left"][0], json_dict["top_left"][1], lowerright[0], lowerright[1]))
        # prevod na NP array, abych nemusel ukladat fotku
        image_np = np.array(img_croped)
        _, buffer = cv2.imencode('.jpg', image_np)
        image_np = np.asarray(bytearray(buffer), dtype=np.uint8)
    except:
         print("Error pri cropovani fotky")

    pic = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    ret, thresh = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY)
    cv2.imshow('Tresh', thresh)
    imagem = cv2.bitwise_not(thresh)
    contours, hierarchy = cv2.findContours(image=imagem, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)
    image_copy = pic.copy()
    cv2.drawContours(image_copy, contours, -1, (0, 255, 0), 2)

    if DEBUG:
        cv2.imshow('Cropped', pic)
        cv2.imshow('Contours', image_copy)
        cv2.imshow("Detected Markers", image)

detect_object(image, detector)


cv2.waitKey(0)
cv2.destroyAllWindows()