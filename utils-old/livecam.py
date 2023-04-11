import numpy as np
import cv2

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

    gcode = []

    for coord in coords:
        x, y = coord
        gcode.append(f"G1 X{round(x, 3)} Y{round(y, 3)} \n")

    gcode.pop(0)
    return gcode

def to_gray(frame, blur1, blur2, tresh1, tresh2):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_smooth = cv2.GaussianBlur(gray, (15, 25), 0)
    _, bin_img = cv2.threshold(gray_smooth, 100, 255, cv2.THRESH_BINARY)
    kernel = np.ones((5, 5), np.uint8)
    bin_img = cv2.morphologyEx(bin_img, cv2.MORPH_CLOSE, kernel, iterations=1)
    ret, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
    return bin_img
