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
LCD_RS = 27
LCD_E  = 15
LCD_D4 = 18
LCD_D5 = 22
LCD_D6 = 23
LCD_D7 = 10

exitBut = 0
clk = 9
dt = 11
encoderBut = 17

#nacteni a inicializace
dictionary, parameters = load_detector()

#deklarace displeje
lcd = rpilcd.CharLCD(pin_rs=LCD_RS, pin_e=LCD_E, pins_data=[LCD_D4, LCD_D5, LCD_D6, LCD_D7], numbering_mode=GPIO.BCM)

printer = Printer("/dev/ttyACM0",210,200)


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
    GPIO.remove_event_detect(encoderBut)
    sleep(0.01)
    event_setup()
    if not lcd_menu.in_manual_mode_menu:
        if lcd_menu.in_led_menu:
            lcd_menu.led_zoff = not lcd_menu.led_zoff
            lcd_menu.update_infopanel()
            
        elif lcd_menu.in_calibration_menu:
            if lcd_menu.line == 0:
                printer.home_startpos()
            if lcd_menu.line == 1:
                lcd_menu.printer_setting()
            
            if lcd_menu.line == 2:
                if lcd_menu.arucoPoint == 0:
                    lcd_menu.arucoFirstPoint()
                    printer.goToCords((0,0))
                elif lcd_menu.arucoPoint == 1:
                    lcd_menu.arucoSecondPoint()
                    printer.goToCords((210,0))
                elif lcd_menu.arucoPoint == 2:
                    lcd_menu.arucoThirdPoint()
                    printer.goToCords((210,210))
                elif lcd_menu.arucoPoint == 3:
                    lcd_menu.arucoCalibDone()
                    printer.goToCords((0,210))
            if lcd_menu.line == 3:
                lcd_menu.sensor_calib(printer)
                
        elif lcd_menu.in_printer_settings:
            line = lcd_menu.line
            if line == 0:
                printer.home()
            elif line == 1:
                printer.goToCords((0,210))
            elif line == 2:
                printer.extruder(-5)
            elif line == 3:
                printer.extruder(5)      
        else:
            lcd_menu.on_click()
    else:
        image = take_picture()
        
        print("START-------------------------------")
        lcd_menu.printing = True
        lcd_menu.print_menu()
        contours, _, pic, json_dict = detect_object(image, dictionary, parameters, DEBUG)
        
        #gcode = con_to_g(contours,pic, json_dict)
        gcode = con_to_gcode(contours,pic, json_dict)
        
        #for line in gcode:
            #print(line)
            
        printer.write_gcodelist(gcode)
        print("END---------------------------------")
        lcd_menu.printing = False
        lcd_menu.manualmode()
    sleep(0.1)
      

#Event na cudl na enkoderu
def event_setup():
    GPIO.add_event_detect(encoderBut,GPIO.RISING,callback=encoder_button_callback, bouncetime=500) 

#Main loop zde
event_setup()
try:
   while True:
       #Exit cudlik handle (event mi nefacha)
       if not GPIO.input(exitBut) and lcd_menu.in_menu and not lcd_menu.printing:
           lcd_menu.on_exit_click()
           lcd_menu.beep()  
       
       if not GPIO.input(exitBut) and lcd_menu.printing:
           lcd_menu.beep()
           lcd_menu.printing = False
           lcd_menu.manualmode()
           printer.stop_print()   
           event_setup() 
           
       #Enkoder a menu handle (hybani se atd)
       clkState = GPIO.input(clk)
       dtState = GPIO.input(dt)
       if clkState != clkLastState:
           if dtState != clkState:
               lcd_menu.moove_down()
               if not lcd_menu.in_menu or lcd_menu.in_calibration_menu or lcd_menu.in_printer_settings: 
                   lcd_menu.beep()
                   
               if lcd_menu.in_led_menu:
                   if lcd_menu.led_zoff:
                       lcd_menu.z_offset += 0.1
                   else:
                       lcd_menu.led_brightness += 1
                   lcd_menu.update_infopanel()
                   lcd_menu.apply_duty()
           else:
               lcd_menu.moove_up()
               if not lcd_menu.in_menu or lcd_menu.in_calibration_menu or lcd_menu.in_printer_settings: 
                   lcd_menu.beep()
                   
               if lcd_menu.in_led_menu:
                   if lcd_menu.led_zoff:
                       lcd_menu.z_offset -= 0.1
                   else:
                       lcd_menu.led_brightness -= 1
                   lcd_menu.update_infopanel()
                   lcd_menu.apply_duty()
       clkLastState = clkState
       sleep(0.01)
#Po exitu se vycisti display a GPIO cleanup
finally:
   lcd.clear()
   sleep(1)
   GPIO.cleanup()



cv2.waitKey(0)
cv2.destroyAllWindows()
