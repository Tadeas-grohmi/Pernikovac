from time import *
import psutil
import threading
import subprocess


class Menu():
    def __init__(self, lcd):
        #promenne
        self.rows = 4
        self.columns = 20
        self.line = 0
        self.connected = "no"
        self.lcd = lcd
        self.update_data = False
        self.lcd_thread = None
        self.led_brightness = 0
        self.in_menu = False
        self.in_led_menu = False
        self.in_manual_mode_menu = False
        self.setup()
    
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
        lcd.cursor_pos = (2, 1)
        lcd.write_string('Auto mode')
        
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
        if not self.in_menu:
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
        if not self.in_menu:
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
        if not self.in_menu:
            self.in_menu = True
            self.lcd.clear()
            self.lcd.home()
            if self.line == 0:
                self.infopanel()
            if self.line == 1:
                self.manualmode()
            if self.line == 2:
                self.automode()
            if self.line == 3:
                self.rpi_info()
    
    #exit handle
    def on_exit_click(self):
        if self.in_menu:
            self.in_menu = False
            self.in_led_menu = False
            self.in_maunal_mode_menu = False
            self.update_data = False
            sleep(0.01)
            self.lcd.clear()
            self.setup()
    
    #prvni render infopanelu
    def infopanel(self):
        self.in_led_menu = True
        self.lcd.write_string(f'LEDky:{self.led_brightness}%')
        self.lcd.cursor_pos = (1,0)
        
        for i in range(0, int(self.led_brightness/5)):
            self.lcd.write_string('\x02')
    
    #render infopanel screen (render led)
    def update_infopanel(self):
        if self.in_led_menu:
            self.lcd.home()
            self.lcd.clear()
            if self.led_brightness >= 100:
                self.led_brightness = 100
            if self.led_brightness <= 0:
                self.led_brightness = 0
                
            self.lcd.write_string(f'LEDky:{self.led_brightness}%')
            self.lcd.cursor_pos = (1,0)
            
            for i in range(0, int(self.led_brightness/5)):
                self.lcd.write_string('\x02')
           
    #render manualmode screen
    def manualmode(self):
        self.lcd.write_string('\x01')
        self.lcd.cursor_pos = (0,1)
        self.lcd.write_string('pernikovac te vita')
        self.lcd.write_string('\x01')
        
        self.lcd.cursor_pos = (1,0)
        self.lcd.write_string('1.Vloz pernicek')
        
        self.lcd.cursor_pos = (2,0)
        self.lcd.write_string('2.Zmackni enkoder')
        
        self.lcd.cursor_pos = (3,0)
        self.lcd.write_string('3.Uzivej pernicek')
    
    #render automode screen
    def automode(self):
        self.lcd.write_string('Comming soon....')
    
    #render Rpi info screeny
    def update_display(self):
        self.update_data = True
        while self.update_data:
            lcd.clear()
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = round(float(f.read()) / 1000.0,1)
            cpu = f"{psutil.cpu_percent()}%"
            
            memory = psutil.virtual_memory()
            available = round(memory.available/1024.0/1024.0,1)
            total = round(memory.total/1024.0/1024.0,1)
            mem_info = f"{available}/{total}"
            used_mem = round((total-available),1)
            
            self.lcd.write_string('hello')
            
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
