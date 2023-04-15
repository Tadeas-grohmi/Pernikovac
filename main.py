import cv2, numpy as np, json, time
from cv2 import *
from utils import printer
# printer = printer.Printer("COM4", (200,200))
# time.sleep(1)
# printer.beep(300,100)
# printer.home()


from PIL import Image
from utils.gcode import *
from utils.math import *
from utils.qrhelper import *

#Promenne
DEBUG = False
json_crop_list = {}

def decode_qr_code(image):
    retval, decoded_info, points, straight_qrcode, image = detect_qrcode(image)
    if retval:
        for i in range(len(points)):
            #extrakce bodu
            qr_corners = points[i].astype(int)
            qr_position, corner_coords = find_qr_corners(qr_corners, image.shape)
            #cmarani pro debug
            if(DEBUG): cv2.rectangle(image, (qr_corners[0][0], qr_corners[0][1]), (qr_corners[2][0], qr_corners[2][1]), (0, 255, 0), 2)

            #check pro spravne rohy
            if qr_position == "Bottom Right":
                lowest_x = 5000
                lowest_y = 5000
                for xpos in qr_corners[:, 0]:
                    if xpos < lowest_x:
                        lowest_x = xpos
                for ypos in qr_corners[:, 1]:
                    if ypos < lowest_y:
                        lowest_y = ypos
                result_coord = [lowest_x, lowest_y]
                if(DEBUG): cv2.circle(image, (lowest_x, lowest_y), 8, (255, 0, 255), -1)
                print(f"Bottom right coords {result_coord}")
                json_dict = {
                    "bottomrightx": lowest_x,
                    "bottomrighty": lowest_y
                }
                json_crop_list.update(json_dict)

            if qr_position == "Bottom Left":
                biggest_x = 0
                lowest_y = 5000
                for xpos in qr_corners[:, 0]:
                    if xpos > biggest_x:
                        biggest_x = xpos
                for ypos in qr_corners[:, 1]:
                    if ypos < lowest_y:
                        lowest_y = ypos
                result_coord = [biggest_x, lowest_y]
                if(DEBUG):cv2.circle(image, (biggest_x, lowest_y), 8, (255, 0, 255), -1)
                print(f"Bottom left coords {result_coord}")
                json_dict = {
                    "bottomleftx" : biggest_x,
                    "bottomlefty" : lowest_y
                }
                json_crop_list.update(json_dict)

            if qr_position == "Upper Right":
                lowest_x = 5000
                biggest_y = 0
                for xpos in qr_corners[:, 0]:
                    if xpos < lowest_x:
                        lowest_x = xpos
                for ypos in qr_corners[:, 1]:
                    if ypos > biggest_y:
                        biggest_y = ypos
                result_coord = [lowest_x, biggest_y]
                if(DEBUG): cv2.circle(image, (lowest_x, biggest_y), 8, (255, 0, 255), -1)
                print(f"Upper right coords {result_coord}")
                json_dict = {
                    "upperrightx": lowest_x,
                    "upperrighty": biggest_y
                }
                json_crop_list.update(json_dict)

            if qr_position == "Upper Left":
                biggest_x = 0
                biggest_y = 0
                for xpos in qr_corners[:, 0]:
                    if xpos > biggest_x:
                        biggest_x = xpos
                for ypos in qr_corners[:, 1]:
                    if ypos > biggest_y:
                        biggest_y = ypos
                result_coord = [biggest_x, biggest_y]
                if(DEBUG): cv2.circle(image, (biggest_x, biggest_y), 8, (255, 0, 255), -1)
                print(f"Upper left coords {result_coord}")
                json_dict = {
                    "upperleftx": biggest_x,
                    "upperlefty": biggest_y
                }
                json_crop_list.update(json_dict)

            #vykresleni rohu
            if(DEBUG):
                for corner in qr_corners:
                    cv2.circle(image, (corner[0], corner[1]), 5, (0, 0, 255), -1)

    #JSON rozklicovani
    bottomleftx = json_crop_list["bottomleftx"]
    bottomlefty = json_crop_list["bottomlefty"]

    upperrightx = json_crop_list["upperrightx"]
    upperrighty = json_crop_list["upperrighty"]

    upperleftx = json_crop_list["upperleftx"]
    upperlefty = json_crop_list["upperlefty"]

    bottomleft = [json_crop_list["bottomleftx"], json_crop_list["bottomlefty"]]
    upperright = [json_crop_list["upperrightx"], json_crop_list["upperrighty"] ]
    upperleft = [json_crop_list["upperleftx"], json_crop_list["upperlefty"]]

    # X,Y 4 rohu ctverce
    x, y = calculate_fourth_point(upperleftx, upperlefty, upperrightx, upperrighty, bottomleftx, bottomlefty)
    lowerright = [int(x), int(y)]

    # debug cmarani
    if (DEBUG):
        cv2.line(image, (upperleft), (upperright), (0, 255, 0), thickness=3, lineType=8)
        cv2.line(image, (upperleft), (bottomleft), (0, 255, 0), thickness=3, lineType=8)
        cv2.line(image, (bottomleft), (lowerright), (0, 255, 0), thickness=3, lineType=8)
        cv2.line(image, (upperright), (lowerright), (0, 255, 0), thickness=3, lineType=8)

    # debug image
    cv2.imshow('QR Codes', image)

    # Try crop fotky ze 4 bodu
    try:
        pil_img = Image.fromarray(image)
        img_croped = pil_img.crop((upperleftx, upperlefty, lowerright[0], lowerright[1]))
        #prevod na NP array, abych nemusel ukladat fotku
        image_np = np.array(img_croped)
        _, buffer = cv2.imencode('.jpg', image_np)
        image_np = np.asarray(bytearray(buffer), dtype=np.uint8)
    except:
        return print("Error pri cropovani fotky")

    # Contour detekce s array fotky
    pic = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    ret, thresh = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY)
    imagem = cv2.bitwise_not(thresh)
    contours, hierarchy = cv2.findContours(image=imagem, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)
    image_copy = pic.copy()
    cv2.drawContours(image_copy, contours, -1, (0, 255, 0), 2)
    cv2.imshow('thresh', image_copy)



image = detect_3_qr_code()
decode_qr_code(image)

#Aby se cv2 nezaviral
cv2.waitKey(0)
cv2.destroyAllWindows()


