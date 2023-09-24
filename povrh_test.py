import cv2
import numpy
import numpy as np
import time
from utils.arucoHelper import *
from utils.math import *
from PIL import Image
from sklearn.cluster import KMeans



pic = cv2.imread("C:/Users/tadea/Pictures/Screenshots/TEST5.png")
gray = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (5, 5), 0)
ret, thresh = cv2.threshold(gray, 138, 255, cv2.THRESH_BINARY)
imagem = cv2.bitwise_not(thresh)
contours, hierarchy = cv2.findContours(image=imagem, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)
image_copy = pic.copy()
cv2.drawContours(image_copy, contours, -1, (0, 255, 0), 2)

for i in contours:
    M = cv2.moments(i)
    if M['m00'] != 0:
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        cv2.drawContours(image_copy, [i], -1, (0, 255, 0), 2)
        cv2.circle(image_copy, (cx, cy), 7, (0, 0, 255), -1)
        break


cv2.imshow('GRAY', gray)
cv2.imshow('Tresh', imagem)
cv2.imshow('Contorus', image_copy)

cv2.waitKey(0)
cv2.destroyAllWindows()