import RPi.GPIO as GPIO
from time import *
import RPILCD.gpio as rpilcd
import psutil
import threading
import subprocess
from utils.utils import *

#promenne UI
BuzzerPin = 12
encoderBut = 17
exitBut = 0
clk = 9
dt = 11
ledpin = 13

class Menu():
    def __init__(self, lcd):
        
        #GPIO settings
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(BuzzerPin, GPIO.OUT, initial=GPIO.LOW) 
        GPIO.setup(encoderBut, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(exitBut, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        clkLastState = GPIO.input(clk)
        self.Buzz = GPIO.PWM(BuzzerPin, 400)
        GPIO.setup(ledpin,GPIO.OUT)
        self.led = GPIO.PWM(ledpin,10000)
        self.led.start(0)

        #promenne
        self.rows = 4
        self.columns = 20
        self.line = 0
        self.connected = "no"
        self.lcd = lcd
        self.update_data = False
        self.lcd_thread = None
        self.in_menu = False
        self.in_led_menu = False
        self.in_manual_mode_menu = False
        self.in_setup_menu = False 
        self.in_calibration_menu = False # Kalibracni menu
        self.locked = False # Zamkly displej
        self.cursorLocked = False #Zamkly cursor
        self.arucoCalib = False # If je v aurco menu
        self.info_line = 0 #Lajna v info panelu
        self.update_sensor = False
        self.printing = False
        self.in_printer_settings = False
        self.shape = 0 # 0-basic, 1-double
        #promenne s zmenou
        self.led_brightness = 0
        self.z_offset = 0
        self.extruder_rate = 0
        self.arucoPoint = 0 
        
        #vedlejsi promenne
        #/home/pi/Desktop/Pernikovac/utils/
        #python /home/pi/Desktop/Pernikovac/main.py
        self.json_file = '/home/pi/Desktop/Pernikovac/utils/data.json'
        
        #nacteni promennych 
        self.json_data = read_json(self.json_file)
        self.led_brightness = self.json_data["led_brightness"]
        self.z_offset = self.json_data["z_offset"]
        self.extruder_rate = self.json_data["extruder_rate"]
        self.apply_duty()
        
        self.setup()
        
    #cudl na enkoderu 
    def encoder_button_callback(self,channel):
        self.on_click() 
    
    #handle pipaku
    def beep(self):
        self.Buzz.start(10)
        sleep(0.01)
        self.Buzz.stop()
    
    #setup screeny, deklarace custom charakteru
    def setup(self):
        self.lcd.clear()
        self.lcd.cursor_pos = (self.line, 0)
        self.lcd.write_string('>')
        
        sleep(0.01)
        self.lcd.cursor_pos = (0, 1)
        self.lcd.write_string('Info panel')
        
        sleep(0.01)
        self.lcd.cursor_pos = (1, 1)
        self.lcd.write_string('Manual mode')
        
        sleep(0.01)
        self.lcd.cursor_pos = (2, 1)
        self.lcd.write_string('Kalibrace')
        
        sleep(0.01)
        self.lcd.cursor_pos = (3, 1)
        self.lcd.write_string('Rpi info')
        
        #Custom char
        celsius = (
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b01110,
            0b00000,
            0b00000,
            0b00000
        )
        
        pernicek = (
            0b01110,
            0b10001,
            0b01110,
            0b00100,
            0b11111,
            0b00100,
            0b01010,
            0b10001
        )
        
        led = (
            0b01110,
            0b11111,
            0b11111,
            0b11111,
            0b01110,
            0b01010,
            0b01010,
            0b00100
        )
        
        self.lcd.create_char(0, celsius)
        self.lcd.create_char(1, pernicek)
        self.lcd.create_char(2, led)
        
    
    #pohyb dolu v menu
    def moove_down(self):
        if not self.in_menu or self.in_calibration_menu or self.in_printer_settings and not self.locked and not self.cursorLocked:
            self.lcd.cursor_pos = (self.line, 0)
            self.lcd.write_string(' ')
            sleep(0.01)
            self.line += 1
            if self.line > 3:
                self.line = 3
            self.lcd.cursor_pos = (self.line, 0)
            self.lcd.write_string('>')
    
    #pohyb nahoru v menu
    def moove_up(self):
        if not self.in_menu or self.in_calibration_menu or self.in_printer_settings and not self.locked and not self.cursorLocked:
            self.lcd.cursor_pos = (self.line, 0)
            self.lcd.write_string(' ')
            sleep(0.01)
            self.line -= 1
            if self.line < 0:
                self.line = 0
            self.lcd.cursor_pos = (self.line, 0)
            self.lcd.write_string('>')
    
    #enkoder klik handle
    def on_click(self):
        if not self.in_menu and not self.locked:
            self.in_menu = True
            self.lcd.clear()
            self.lcd.home()
            if self.line == 0:
                self.infopanel()
            if self.line == 1:
                self.manualmode()
            if self.line == 2:
                self.kalibrace()
            if self.line == 3:
                self.rpi_info()
    
    #Zapis do json
    def write_data(self):
        self.json_data["led_brightness"] = self.led_brightness
        self.json_data["z_offset"] = self.z_offset
        self.json_data["extruder_rate"] = self.extruder_rate
        write_json(self.json_file, self.json_data)
    
    #exit handle
    def on_exit_click(self):
        if self.in_menu and not self.locked and not self.printing:
            self.in_menu = False
            self.in_led_menu = False
            self.in_manual_mode_menu = False
            self.in_calibration_menu = False
            self.cursorLocked = False
            self.update_data = False
            self.update_sensor = False
            self.in_printer_settings = False
            self.info_line = 0
            self.line = 0
            sleep(0.01)
            self.lcd.clear()
            self.setup()
            self.write_data()
    
    #prvni render infopanelu
    def infopanel(self):
        self.in_led_menu = True
        self.lcd.cursor_pos = (0,1)
        self.lcd.write_string(f'LEDky:{self.led_brightness}%')
        
        match self.info_line:
                case 0:
                    self.lcd.cursor_pos = (0,0)
                    self.lcd.write_string(f'>')
                case 1:
                    self.lcd.cursor_pos = (2,0)
                    self.lcd.write_string(f'>')
                case 2:
                    self.lcd.cursor_pos = (3,0)
                    self.lcd.write_string(f'>')
        
        self.lcd.cursor_pos = (1,0)
        for i in range(0, int(self.led_brightness/5)):
            self.lcd.write_string('\x02')
        
        self.lcd.cursor_pos = (2,1)
        self.lcd.write_string(f'Extruder rate:{round(self.extruder_rate, 2)}')
        
        self.lcd.cursor_pos = (3,1)
        self.lcd.write_string(f'Z-offset:{round(self.z_offset, 1)}mm')
    
    #render infopanel screen (render led)
    def update_infopanel(self):
        if self.in_led_menu:
            self.lcd.home()
            self.lcd.clear()
            if self.led_brightness >= 100:
                self.led_brightness = 100
            if self.led_brightness <= 0:
                self.led_brightness = 0
            
            if self.z_offset <= 0:
                self.z_offset = 0.0
            
            if self.extruder_rate <=0:
                self.extruder_rate = 0.0
            
            match self.info_line:
                case 0:
                    self.lcd.cursor_pos = (0,0)
                    self.lcd.write_string(f'>')
                case 1:
                    self.lcd.cursor_pos = (2,0)
                    self.lcd.write_string(f'>')
                case 2:
                    self.lcd.cursor_pos = (3,0)
                    self.lcd.write_string(f'>')
            
            self.lcd.cursor_pos = (0,1)
            self.lcd.write_string(f'LEDky:{self.led_brightness}%')
            self.lcd.cursor_pos = (1,0)
            
            for i in range(0, int(self.led_brightness/5)):
                self.lcd.write_string('\x02')
            
            self.lcd.cursor_pos = (2,1)
            self.lcd.write_string(f'Extruder rate:{round(self.extruder_rate, 2)}')
            
            self.lcd.cursor_pos = (3,1)
            self.lcd.write_string(f'Z-offset:{round(self.z_offset, 1)}mm')
           
    #render manualmode screen
    def manualmode(self):
        self.lcd.clear()
        self.in_manual_mode_menu = True
        #self.lcd.write_string('\x01')
        #self.lcd.cursor_pos = (0,1)
        #self.lcd.write_string('pernikovac te vita')
        #self.lcd.write_string('\x01')
        self.lcd.cursor_pos = (0,0)
        self.lcd.write_string('Motiv:')
        self.lcd.cursor_pos = (0,6)
        match self.shape:
            case 0:
                self.lcd.write_string('klasik')
            case 1:
                self.lcd.write_string('double')
            
        self.lcd.cursor_pos = (1,0)
        self.lcd.write_string('1.Vloz pernicek')
        
        self.lcd.cursor_pos = (2,0)
        self.lcd.write_string('2.Zmackni enkoder')
        
        self.lcd.cursor_pos = (3,0)
        self.lcd.write_string('3.Uzivej pernicek')
    
    def update_manualmode(self):
        if self.in_manual_mode_menu:
            self.lcd.clear()
            self.lcd.cursor_pos = (0,0)
            self.lcd.write_string('Motiv:')
            self.lcd.cursor_pos = (0,6)
            match self.shape:
                case 0:
                    self.lcd.write_string('klasik')
                case 1:
                    self.lcd.write_string('double')
                
            self.lcd.cursor_pos = (1,0)
            self.lcd.write_string('1.Vloz pernicek')
            
            self.lcd.cursor_pos = (2,0)
            self.lcd.write_string('2.Zmackni enkoder')
            
            self.lcd.cursor_pos = (3,0)
            self.lcd.write_string('3.Uzivej pernicek')
            
        
        
    #render print menu
    def print_menu(self):
        self.lcd.clear()
        self.lcd.cursor_pos = (0,2)
        self.lcd.write_string('Pernicek se dela')
        self.lcd.cursor_pos = (2,0)
        self.lcd.write_string('E-stop je na krizku!')
    
    #render automode screen
    def automode(self):
        self.lcd.write_string('Comming soon....')
    
    #render tiskarna settings
    def printer_setting(self):
        self.lcd.clear()
        self.in_calibration_menu = False
        self.in_printer_settings = True
        self.lcd.cursor_pos = (self.line, 0)
        self.lcd.write_string('>')
        self.lcd.cursor_pos = (0,1)
        self.lcd.write_string('Posunout na start')
        self.lcd.cursor_pos = (1,1)
        self.lcd.write_string('Kalibrace Z osy')
        self.lcd.cursor_pos = (2,1)
        self.lcd.write_string('Vytlacit trysku')
        self.lcd.cursor_pos = (3,1)
        self.lcd.write_string('Zatlacit trysku')
        
    #render kalibrace menu
    def kalibrace(self):
        self.lcd.clear()
        self.in_calibration_menu = True
        self.line = 0
        self.lcd.cursor_pos = (self.line, 0)
        self.lcd.write_string('>')
        self.lcd.cursor_pos = (0,1)
        self.lcd.write_string('Home tiskarny')
        self.lcd.cursor_pos = (1,1)
        self.lcd.write_string('Nastaveni tiskarny')
        self.lcd.cursor_pos = (2,1)
        self.lcd.write_string('Kalibrace ARUCO')
        self.lcd.cursor_pos = (3,1)
        self.lcd.write_string('Test senzoru')
        
    def arucoFirstPoint(self):
        self.cursorLocked = True
        self.arucoCalib = True
        self.arucoPoint = 1
        self.lcd.clear()
        self.lcd.cursor_pos = (0,0)
        self.lcd.write_string('Nastav prvni roh')
        self.lcd.cursor_pos = (1,0)
        self.lcd.write_string('Stiskni enkoder pro dalsi bod')
    
    def arucoSecondPoint(self):
        self.arucoPoint = 2
        self.lcd.clear()
        self.lcd.cursor_pos = (0,0)
        self.lcd.write_string('Nastav druhy roh')
        self.lcd.cursor_pos = (1,0)
        self.lcd.write_string('Stiskni enkoder pro dalsi bod')
    
    def arucoThirdPoint(self):
        self.arucoPoint = 3
        self.lcd.clear()
        self.lcd.cursor_pos = (0,0)
        self.lcd.write_string('Nastav treti roh')
        self.lcd.cursor_pos = (1,0)
        self.lcd.write_string('Stiskni enkoder pro dalsi bod')
        
    def arucoCalibDone(self):
        self.arucoCalib = False
        self.arucoPoint = 0
        self.cursorLocked = False
        self.lcd.clear()
        self.lcd.cursor_pos = (0,0)
        self.lcd.write_string('Hotovo')
    
    #render senzor kalibrace
    def sensor_calib(self, printer):
        self.update_sensor = True
        self.cursorLocked = True
        while self.update_sensor:
            self.lcd.clear()
            self.lcd.cursor_pos = (0,0)
            self.lcd.write_string(f"TOF senzor: 699mm")
            self.lcd.cursor_pos = (1,0)
            self.lcd.write_string(f"hot end: 185")
            self.lcd.write_string('\x00')
            self.lcd.write_string('C')
            self.lcd.cursor_pos = (2,0)
            self.lcd.write_string(f"BED temp: 215")
            self.lcd.write_string('\x00')
            self.lcd.write_string('C')
            sleep(1)
    
    #LEDky - apliakce duty 
    def apply_duty(self):
        self.led.ChangeDutyCycle(self.led_brightness)
    
    #render Rpi info screeny
    def update_display(self):
        self.update_data = True
        while self.update_data:
            self.lcd.clear()
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = round(float(f.read()) / 1000.0,1)
            cpu = f"{psutil.cpu_percent()}%"
            
            memory = psutil.virtual_memory()
            available = round(memory.available/1024.0/1024.0,1)
            total = round(memory.total/1024.0/1024.0,1)
            mem_info = f"{available}/{total}"
            used_mem = round((total-available),1)
            
            self.lcd.cursor_pos = (0,0)
            self.lcd.write_string(f"Teplota:{temp}")
            self.lcd.write_string('\x00')
            self.lcd.write_string('C')
            
            self.lcd.cursor_pos = (1,0)
            self.lcd.write_string(f"CPU:{cpu}")
            
            self.lcd.cursor_pos = (2,0)
            self.lcd.write_string(f"RAM:{used_mem}MB")
            sleep(1)
    
    #Screen pro rpi info (thread start)
    def rpi_info(self):
        self.lcd_thread = threading.Thread(target=self.update_display)
        self.lcd_thread.start()
