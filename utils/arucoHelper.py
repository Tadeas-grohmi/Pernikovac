import cv2
import numpy as np


def load_detector():
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    return detector

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


def detect_3_aruco_code(detector):
    led_bright = 0
    while True:
        # Capture a Full HD photo
        photo = take_picture()

        # Detect QR codes in the photo
        _, markerIds,_ = detector.detectMarkers(photo)

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