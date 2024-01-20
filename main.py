#Made by Tadeas-grohmi with love <3
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
from utils.VLX.VL53L0X_python.python import VL53L0X
from utils.shapes import *

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

#promenne cudlu 
exitBut = 0
clk = 9
dt = 11
encoderBut = 17

#nacteni a inicializace
dictionary, parameters = load_detector()

#deklarace displeje
lcd = rpilcd.CharLCD(pin_rs=LCD_RS, pin_e=LCD_E, pins_data=[LCD_D4, LCD_D5, LCD_D6, LCD_D7], numbering_mode=GPIO.BCM)

#Nacteni tiskarny
printer = Printer("/dev/ttyACM0",215,200)

#Nacteni TOF senzoru
tof = VL53L0X.VL53L0X(i2c_bus=1,i2c_address=0x29)
tof.open() 

#LCD menu deklarace
lcd_menu = Menu(lcd)
clkLastState = GPIO.input(clk)

#cudl na enkoderu 
def encoder_button_callback(channel):
    #GPIO.remove_event_detect(encoderBut)
    #event_setup()
    if not lcd_menu.in_manual_mode_menu:
        #Info panel
        if lcd_menu.in_led_menu:
            lcd_menu.info_line += 1
            if lcd_menu.info_line > 2:
                lcd_menu.info_line = 0

            lcd_menu.update_infopanel()
            
        #Kalibracni menu
        elif lcd_menu.in_calibration_menu:
            #Home + start pozice
            if lcd_menu.line == 0:
                printer.home_startpos()
            #Tiskarna settings
            if lcd_menu.line == 1:
                lcd_menu.printer_setting()
            #Aruco kalibrace
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
            #Senozr kalibrace
            if lcd_menu.line == 3:
                lcd_menu.sensor_calib(printer)
        #Printer settings menu
        elif lcd_menu.in_printer_settings:
            line = lcd_menu.line
            if line == 0:
                printer.goToCords((0,210))
            elif line == 1:
                image = take_picture()
                _, _, pic, json_dict, middle_point = detect_object(image, dictionary, parameters, DEBUG)
                tof.start_ranging(VL53L0X.Vl53l0xAccuracyMode.BEST)
                zoff = printer.get_z(json_dict, middle_point, pic, tof)
                tof.stop_ranging()
                lcd_menu.z_offset = zoff
                lcd_menu.write_data()
            elif line == 2:
                printer.extruder(-10)
            elif line == 3:
                printer.extruder(5)      
        else:
            lcd_menu.on_click()
    #Manual mode aka zdobeni 
    else:
        try:
            image = take_picture()
            
            print("START-------------------------------")
            lcd_menu.printing = True
            lcd_menu.print_menu()
            contours, _, pic, json_dict, middle_point = detect_object(image, dictionary, parameters, DEBUG)
            
            match lcd_menu.shape:
                case 0: #Klasika
                    contours = contours
                case 1: #Double
                    contours = double(contours,middle_point, pic)
            
            gcode = con_to_gcode(contours,pic, json_dict, lcd_menu.extruder_rate, lcd_menu.z_offset)
            
            for line in gcode:
                print(line)
                
            printer.shake() #Bordel z trysky pryc
            printer.write_gcodelist(gcode)
            print("END---------------------------------")
            lcd_menu.printing = False
            lcd_menu.manualmode()
        except Exception as e:
            print(f"An exception occurred: {e}")
            lcd_menu.printing = False
            lcd_menu.manualmode()
      

#Event na cudl na enkoderu
def event_setup():
    GPIO.add_event_detect(encoderBut,GPIO.RISING,callback=encoder_button_callback, bouncetime=650) 

#Main loop zde
event_setup()
try:
   while True:
       #Exit cudlik handle (event mi nefacha)
       if not GPIO.input(exitBut) and lcd_menu.in_menu and not lcd_menu.printing:
           lcd_menu.on_exit_click()
           lcd_menu.beep()  
       #E-stop
       if not GPIO.input(exitBut) and lcd_menu.printing:
           lcd_menu.beep()
           lcd_menu.printing = False
           lcd_menu.manualmode()
           printer.stop_print()   
           #event_setup() 
           
       #Enkoder a menu handle (hybani se atd)
       clkState = GPIO.input(clk)
       dtState = GPIO.input(dt)
       if clkState != clkLastState:
           if dtState != clkState:
               #Pohyb dolu
               lcd_menu.moove_down()
               #Beep handle
               if not lcd_menu.in_menu or lcd_menu.in_calibration_menu or lcd_menu.in_printer_settings: 
                   lcd_menu.beep()
               #Handle zvetseni hodnot
               if lcd_menu.in_led_menu:
                   match lcd_menu.info_line:
                      case 0:
                          lcd_menu.led_brightness += 1
                      case 1:
                          lcd_menu.extruder_rate += 0.01
                      case 2:
                          lcd_menu.z_offset += 0.1
               
                   #Update a write hodnot
                   lcd_menu.update_infopanel()
                   lcd_menu.apply_duty()
               #Handle zmeny tvaru
               if lcd_menu.in_manual_mode_menu and not lcd_menu.printing:
                   lcd_menu.shape -= 1
                   if lcd_menu.shape < 0:
                       lcd_menu.shape = 0
                   
                   lcd_menu.update_manualmode()
           else:
               #Pohyb nahoru
               lcd_menu.moove_up()
               #Beep handle
               if not lcd_menu.in_menu or lcd_menu.in_calibration_menu or lcd_menu.in_printer_settings: 
                   lcd_menu.beep()
               #Handle zvetseni hodnot
               if lcd_menu.in_led_menu:
                   match lcd_menu.info_line:
                      case 0:
                          lcd_menu.led_brightness -= 1
                      case 1:
                          lcd_menu.extruder_rate -= 0.01
                      case 2:
                          lcd_menu.z_offset -= 0.1
               
                   #Update a write hodnot
                   lcd_menu.update_infopanel()
                   lcd_menu.apply_duty()
               #Handle zmeny tvaru
               if lcd_menu.in_manual_mode_menu and not lcd_menu.printing:
                   lcd_menu.shape += 1
                   if lcd_menu.shape > 1:
                       lcd_menu.shape = 1
                   
                   lcd_menu.update_manualmode()
       #Ende
       clkLastState = clkState
       sleep(0.02)

except KeyboardInterrupt:
    lcd.clear()

#Po exitu se vycisti display a GPIO cleanup
finally:
    lcd.clear()
    tof.close()
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    sleep(2)
    GPIO.cleanup()

