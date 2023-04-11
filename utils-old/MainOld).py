import time, cv2
from utils import printer

from utils.livecam import *

printer = printer.Printer("COM12", (200, 200))
time.sleep(1)
printer.beep(300,100)

video_capture = cv2.VideoCapture(0)

def main_loop():
    homed = 0
    printing = False
    global check

    while video_capture.isOpened():
        if homed == 0:
            printer.home()
            printer.elevateZ()
            homed = 1

        if printing == False:

            # Captures video_capture frame by frame
            _, frame = video_capture.read()

            bin_img = to_gray(frame, 15, 25, 100, 255)
            cv2.imshow('BIN_IMG', bin_img)

            contours, hierarchy = cv2.findContours(image=bin_img, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)

            image_copy = frame.copy()
            try:
                cv2.drawContours(image=image_copy, contours=[filter_frame(contours)], contourIdx=-1, color=(0, 255, 0),
                                 thickness=1,
                                 lineType=cv2.LINE_AA)
                cv2.imshow('Detekce', image_copy)
            except:
                print("None")

            if cv2.waitKey(1) & 0xff == ord('q'):
                break

            if cv2.waitKey(1) & 0xff == ord('w'):
                list = contours_to_gcode(contours)
                check = printer.write_gcodelist(list)
                printing = True

        if printing == True and check == "DONE":
            printing = False


if __name__ == "__main__":
    main_loop()


video_capture.release()
cv2.destroyAllWindows()



