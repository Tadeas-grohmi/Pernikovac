import numpy as np
import cv2

def get_contour_coords(contours):
    coords = []
    for contour in contours:
        for point in contour:
            x, y = point[0]
            coords.append([x, y])
    return coords

def contours_to_gcode(contours):
    coords = []

    for contour in contours:
        for point in contour:
            x, y = point[0]
            coords.append([x, y])
    # Scale down coordinates
    coords = np.array(coords)
    coords = coords * (200 / np.max(coords))
    coords = coords[4:]
    # Create G-code
    gcode = "G28 \n" # move to home position
    gcode += "G1 Z5 F500 \n" #move up
    gcode += "G1 F500 \n"
    for coord in coords:
        x, y = coord
        gcode += f"G1 X{round(x, 3)} Y{round(y, 3)} \n"
    gcode += "G28 \n" # move to home position
    gcode += "G1 Z5 F500 \n" #move up
    return gcode

def rescale(image):
    scale_percent = 40  # percent of original size
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    frame = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    return frame

def filter_frame(contours):
    coords = []
    for contour in contours:
        for point in contour:
            x, y = point[0]
            coords.append([x, y])
    # Scale down coordinates
    coords = np.array(coords)
    coords = coords[4:]
    return coords

frame = rescale(cv2.imread('ddd.png'))
cv2.imshow("CUM",frame)

#G(r)ay scale
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
gray_smooth = cv2.GaussianBlur(gray, (15, 15), 0)
_, bin_img = cv2.threshold(gray_smooth, 100, 255, cv2.THRESH_BINARY)
kernel = np.ones((3, 3), np.uint8)
bin_img = cv2.morphologyEx(bin_img, cv2.MORPH_CLOSE,kernel, iterations=10)
ret, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

#Contours
contours, hierarchy = cv2.findContours(image=bin_img, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)

#Writing to img
image_copy = frame.copy()
cv2.drawContours(image=image_copy, contours=[filter_frame(contours)], contourIdx=-1, color=(255, 255, 0), thickness=2,
                 lineType=cv2.LINE_AA)

cv2.imshow('Contoury', image_copy)



