import cv2
import numpy
import numpy as np
import time
from utils.arucoHelper import *
from utils.math import *
from utils.gcode import *
from PIL import Image
import random


def double(contours, middle_point, pic):
    middle_point = np.array(middle_point)
    npcontours = np.array(contours)

    vector_to_middle = middle_point - npcontours
    scaling_factor = 0.55

    new_contours = npcontours + vector_to_middle * scaling_factor
    new_contours = new_contours.reshape((-1, 1, 2)).astype(np.int32)

    arr1 = npcontours.reshape((npcontours.shape[0], 1, 2))
    arr2 = new_contours.reshape((new_contours.shape[0], 1, 2))

    combined_array = np.concatenate((arr1, arr2), axis=0)
    combined_array = [[[[x, y]]] for [[x, y]] in combined_array]

    cv2.polylines(pic, [new_contours], isClosed=True, color=(0, 10, 205), thickness=1)

    return combined_array