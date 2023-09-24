import cv2
import numpy as np
from PIL import Image
from cv2 import aruco
from utils.math import *

def load_detector():
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
    parameters = cv2.aruco.DetectorParameters_create()

    return dictionary, parameters

def ArucoPoints(markerCorners, markerIds, image, DEBUG):
    corner_list = []
    midPoint_list = []

    if markerIds is not None:
        for i in range(len(markerIds)):
            markerCorner = markerCorners[i][0]

            append_list = []
            for corner in markerCorner:
                append_list.append([int(corner[0]), int(corner[1])])

                if DEBUG:
                    cv2.circle(image, (int(corner[0]), int(corner[1])), 5, (0, 255, 255), -1)

            # Calculate the centroid of the marker
            cx = int((markerCorner[0][0] + markerCorner[2][0]) / 2)
            cy = int((markerCorner[0][1] + markerCorner[2][1]) / 2)

            midPoint_list.append([cx, cy])

            # Draw a point on the centroid of the marker
            if DEBUG:
                cv2.circle(image, (cx, cy), 5, (0, 255, 0), -1)
            corner_list.append(append_list)

        return corner_list, midPoint_list

#Bottom right corner
def bottom_right_corner(corner_coords):
    corner_coords = np.array(corner_coords)
    # Find the index of the bottom-right corner
    bottom_right_index = np.argmax(corner_coords.sum(axis=1))
    bottom_right_corner = corner_coords[bottom_right_index]
    return list(bottom_right_corner)

#bottom left corner
def bottom_left_corner(corner_coords):
    corner_coords = np.array(corner_coords)
    # Find the index of the bottom-left corner
    bottom_left_index = np.argmin(corner_coords[:, 0])
    bottom_left_corner = corner_coords[bottom_left_index]
    return list(bottom_left_corner)

#Calculate the posionts of the points

def crop_coords(image, midPointList,cornerList, DEBUG):
    image_shape = image.shape
    image_width = image_shape[1]
    image_height = image_shape[0]

    json_dict = {
        "top_left": [],
        "top_right": [],
        "bottom_left": [],
    }

    for i in range(len(midPointList)):
        x = midPointList[i][0]
        y = midPointList[i][1]

        if x < image_width/2 and y < image_height/2:
            json_dict["top_left"] = bottom_right_corner(cornerList[i])

        if x > image_width/2 and y < image_height/2:
            json_dict["top_right"] = bottom_left_corner(cornerList[i])

        if x < image_width/2 and y > image_height/2:
            json_dict["bottom_left"] = bottom_right_corner(cornerList[i])

    if DEBUG:
        for coords in json_dict.values():
            cv2.circle(image, (coords[0], coords[1]), 5, (255, 255, 0), -1)

    return json_dict


def detect_3_aruco_code(dictionary, parameters):
    led_bright = 0
    while True:
        # Capture a Full HD photo
        photo = take_picture()

        # Detect QR codes in the photo
        #_, markerIds,_ = detector.detectMarkers(photo)
        _, markerIds, _ = aruco.detectMarkers(photo, dictionary, parameters=parameters)

        # Check if exactly 3 QR codes were detected
        if len(markerIds) == 3:
            print("3 QR codes detected!")
            return photo
        else:
            led_bright += 5
            print(f"Detected {len(markerIds)} QR codes. Retrying...")
            
def take_picture():
    #prvni foto
    cap = cv2.VideoCapture(0)
    #full hd rozliseni
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    #ukladani
    result, image = cap.read()
    cap.release()
    return image


def crop_pic(json_dict,lowerright, image):
    try:
        pil_img = Image.fromarray(image)
        img_croped = pil_img.crop((json_dict["top_left"][0], json_dict["top_left"][1], lowerright[0], lowerright[1]))
        # prevod na NP array, abych nemusel ukladat fotku
        image_np = np.array(img_croped)
        _, buffer = cv2.imencode('.jpg', image_np)
        image_np = np.asarray(bytearray(buffer), dtype=np.uint8)
        return image_np
    except:
        print("Error pri cropovani fotky")

def get_contours(image_np, DEBUG):
    pic = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    ret, thresh = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY)
    imagem = cv2.bitwise_not(thresh)
    contours, hierarchy = cv2.findContours(image=imagem, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)
    image_copy = pic.copy()
    if DEBUG:
        cv2.imshow('Tresh', thresh)
        cv2.drawContours(image_copy, contours, -1, (0, 255, 0), 2)

    return contours, pic, image_copy

def detect_object(image, dictionary, parameters, DEBUG):

    #markerCorners, markerIds, rejectedCandidates = detector.detectMarkers(image)
    
    markerCorners, markerIds, rejectedImgPoints = aruco.detectMarkers(image, dictionary, parameters=parameters)
    
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
    
    return contours, pic, image_copy





