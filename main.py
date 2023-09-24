import cv2
import numpy
import numpy as np
import time
from utils.arucoHelper import *
from utils.math import *
from PIL import Image
from utils.printer import *
from utils.lcdmenu import *
from utils.gcode import *
import RPILCD.gpio as rpilcd
#Promenne
DEBUG = False
Calibration = False

#promenne displeje
LCD_RS = 9
LCD_E  = 11
LCD_D4 = 10
LCD_D5 = 22
LCD_D6 = 17
LCD_D7 = 27

exitBut = 12
clk = 21
dt = 20
encoderBut = 6

#nacteni a inicializace
image = cv2.imread("test3.jpg")
dictionary, parameters = load_detector()

#deklarace displeje
lcd = rpilcd.CharLCD(pin_rs=LCD_RS, pin_e=LCD_E, pins_data=[LCD_D4, LCD_D5, LCD_D6, LCD_D7], numbering_mode=GPIO.BCM)

# while not Calibration:
#     detect_3_aruco_code(detector)
#     #printer.home()
#     
# detect_object(image, detector)

#LCD menu deklarace
lcd_menu = Menu(lcd)
clkLastState = GPIO.input(clk)

#cudl na enkoderu 
def encoder_button_callback(channel):
    if not lcd_menu.in_manual_mode_menu:
        if lcd_menu.in_led_menu:
            lcd_menu.led_zoff = not lcd_menu.led_zoff
            lcd_menu.update_infopanel()
        elif lcd_menu.in_calibration_menu:
            print(lcd_menu.line)
        else:
            lcd_menu.on_click()
    else:
        print("START-------------------------------")
        contours, _, _ = detect_object(image, dictionary, parameters, DEBUG)
        gcode = contours_to_gcode(contours)
        
        for line in gcode:
            print(line)
        
        print("END---------------------------------")
    
    sleep(0.01)
      

#Event na cudl na enkoderu
GPIO.add_event_detect(encoderBut,GPIO.RISING,callback=encoder_button_callback, bouncetime=200) 

#Main loop zde
try:
   while True:
       #Exit cudlik handle (event mi nefacha)
       if not GPIO.input(exitBut) and lcd_menu.in_menu:
           lcd_menu.on_exit_click()
       
       #Enkoder a menu handle (hybani se atd)
       clkState = GPIO.input(clk)
       dtState = GPIO.input(dt)
       if clkState != clkLastState:
           if dtState != clkState:
               lcd_menu.moove_down()
               if not lcd_menu.in_menu: 
                   lcd_menu.beep()
               if lcd_menu.in_led_menu:
                   if lcd_menu.led_zoff:
                       lcd_menu.z_offset += 0.1
                   else:
                       lcd_menu.led_brightness += 1
                   lcd_menu.update_infopanel()
           else:
               lcd_menu.moove_up()
               if not lcd_menu.in_menu: 
                   lcd_menu.beep()
               if lcd_menu.in_led_menu:
                   if lcd_menu.led_zoff:
                       lcd_menu.z_offset -= 0.1
                   else:
                       lcd_menu.led_brightness -= 1
                   lcd_menu.update_infopanel()
       clkLastState = clkState
       sleep(0.01)
#Po exitu se vycisti display a GPIO cleanup
finally:
   lcd.clear()
   sleep(1)
   GPIO.cleanup()



cv2.waitKey(0)
cv2.destroyAllWindows()
