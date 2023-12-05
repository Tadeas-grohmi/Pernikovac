import cv2
import numpy as np
from PIL import Image
from cv2 import aruco
from utils.math import *

#Load detektoru pro aruco (novy python)
def load_detector():
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
    parameters = cv2.aruco.DetectorParameters()

    return dictionary, parameters

#Detekce aruco bodu
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
                    cv2.circle(image, (int(corner[0]), int(corner[1])), 3, (0, 255, 255), -1)

            # Calculate the centroid of the marker
            cx = int((markerCorner[0][0] + markerCorner[2][0]) / 2)
            cy = int((markerCorner[0][1] + markerCorner[2][1]) / 2)

            midPoint_list.append([cx, cy])

            # Draw a point on the centroid of the marker
            if DEBUG:
                cv2.circle(image, (cx, cy), 3, (0, 255, 0), -1)
            corner_list.append(append_list)

        return corner_list, midPoint_list

#Bottom right corner
def bottom_right_corner(corner_coords):
    corner_coords = np.array(corner_coords)
    bottom_right_index = np.argmax(corner_coords.sum(axis=1))
    bottom_right_corner = corner_coords[bottom_right_index]
    return list(bottom_right_corner)

#bottom left corner
def bottom_left_corner(corner_coords):
    corner_coords = np.array(corner_coords)
    bottom_left_index = np.argmin(corner_coords[:, 0])
    bottom_left_corner = corner_coords[bottom_left_index]
    return list(bottom_left_corner)


#Klasifikace aruco bodu 
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
            cv2.circle(image, (coords[0], coords[1]), 3, (200, 255, 0), -1)

    return json_dict

#Kalibrace na 3 aruco body
def detect_3_aruco_code(dictionary, parameters):
    led_bright = 0
    while True:
        photo = take_picture()
        _, markerIds, _ = aruco.detectMarkers(photo, dictionary, parameters=parameters)
        if len(markerIds) == 3:
            print("3 QR codes detected!")
            return photo
        else:
            led_bright += 5
            print(f"Detected {len(markerIds)} QR codes. Retrying...")
            
#Full HD fotka, return cele image
def take_picture():
    cap = cv2.VideoCapture(0)
    #full hd rozliseni
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    #ukladani
    result, image = cap.read()
    cap.release()
    return image

#Crop fotky z aruco bodu
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

#Ziskani conturu
def get_contours(image_np, DEBUG):
    pic = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    #pic = cv2.rotate(pic, cv2.ROTATE_180)
    gray = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (13, 13), 0)
    
    max_value = 255  # Maximum value for threshold
    block_size = 951  # Size of the neighborhood area
    constant = 23  # Constant subtracted from the mean

    thresh = cv2.adaptiveThreshold(gray, max_value, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size,constant)
    
    imagem = cv2.bitwise_not(thresh)
    contours, hierarchy = cv2.findContours(image=imagem, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)
    image_copy = pic.copy()
    
    x_min = 45  # Minimum X coordinate 45
    x_max = 800  # Maximum X coordinate 800
    y_min = 25  # Minimum Y coordinate 0
    y_max = 765  # Maximum Y coordinate 765 794
    
    #Filtr nepotrebnych conturu (mimo dosah tiskarny)
    filtered_contours = [contour for contour in contours if x_min <= cv2.boundingRect(contour)[0] <= x_max
                         and y_min <= cv2.boundingRect(contour)[1] <= y_max]
    
    for i in filtered_contours:
      M = cv2.moments(i)
      if M['m00'] != 0:
          cx = int(M['m10'] / M['m00'])
          cy = int(M['m01'] / M['m00'])
          middle_point = [cx, cy]
          cv2.circle(image_copy, (cx, cy), 1, (0, 0, 255), 2)
          break

    middle_point = np.array(middle_point)

    npcontours = np.vstack(filtered_contours)

    #Prostredek ze vsech body (vektor)
    vector_to_middle = middle_point - npcontours 

    scaling_factor = 0.2  #Scaling faktor

    #Scaling bodu
    scaled_contour = npcontours + vector_to_middle * scaling_factor
    scaled_contour = scaled_contour.reshape((-1, 1, 2)).astype(np.int32)
    
    if DEBUG:
        cv2.imshow('Tresh', thresh)
        cv2.drawContours(image_copy, filtered_contours, -1, (200, 255, 0), 6)
        cv2.polylines(image_copy, [scaled_contour], isClosed=True, color=(0, 0, 255), thickness=1)
    
    scaled_points = [[[[x, y]]] for [[x, y]] in scaled_contour]
    
    return scaled_points, pic, image_copy, middle_point

#Offsety kdyby bylo potreba
Right_top_offs = [0,0] # [-50,25] [0,-15]
Left_top_offs = [0,0] # [20,30] [0,15]
Left_bottom_offs = [0,0] # [20,0]
Right_bottom_offs = [0,-10] # [10,0]

#Main cast kodu
def detect_object(image, dictionary, parameters, DEBUG):   
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)
    markerCorners, markerIds, rejectedImgPoints = detector.detectMarkers(image)
    
    cornerList, midPointList = ArucoPoints(markerCorners, markerIds, image, DEBUG)
    json_dict = crop_coords(image, midPointList,cornerList, DEBUG)
    json_dict = apply_offset(json_dict, Left_top_offs, Right_top_offs, Left_bottom_offs)

    x, y = calculate_fourth_point(json_dict, Right_bottom_offs)
    lowerright = [int(x), int(y)]

    image_np = crop_pic(json_dict,lowerright, image)

    contours, pic, image_copy, middle_point = get_contours(image_np, DEBUG)

    if DEBUG:
        for coords in json_dict.values():
            cv2.circle(image, (coords[0], coords[1]), 3, (255, 190, 0), -1)
            cv2.circle(image, (lowerright[0], lowerright[1]), 3, (100, 255, 0), -1)
        cv2.imshow('Cropped', pic)
        cv2.imshow('Contours', image_copy)
        cv2.imshow("Detected Markers", image) 
        cv2.imwrite("idk.png", image)
    
    return contours, pic, image_copy, json_dict, middle_point





