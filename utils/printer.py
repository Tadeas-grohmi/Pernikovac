import serial, time
import math
import serial.tools.list_ports

class Printer():
    def __init__(self,COM, bedSizeX,bedSizeY):
        self.COM = COM
        self.max_X = bedSizeX
        self.max_Y = bedSizeY
        self.position = (0,0)
        self.homed = False
        try:
            self.printerSerial = serial.Serial(COM,115200, timeout=25)
            print("Connected")
        except:
            print("Connection error")
            return 

    def WritePoints(self, xy):
        x,y = xy

        command = 'G1 F1500 X%d Y%d\n' % (x, y)

        print(command.encode())

        if self.printerSerial is not None:
            self.printerSerial.write(command.encode())
            return 1
        else:
            return 0

    def home(self):
        if not self.homed:
            self.printerSerial.write(b'G28\n')
            while True:
                response = self.printerSerial.readline().decode().strip()
                if response == 'ok':
                    break
    
            self.homed = True
    
    def extruder(self, pos):
        self.printerSerial.write(b'G92 E0\n')
        while True:
            response = self.printerSerial.readline().decode().strip()
            if response == 'ok':
                break
        self.printerSerial.write('G1 E{} f500\n'.format(pos).encode())
        while True:
            response = self.printerSerial.readline().decode().strip()
            if response == 'ok':
                break
        
    
    def home_startpos(self):
        if not self.homed:
            self.printerSerial.write(b'G28\n')
            while True:
                response = self.printerSerial.readline().decode().strip()
                if response == 'ok':
                    break
        
            self.homed = True
        
        self.printerSerial.write(b'G1 X0 Y210 Z30 F1000\n')
        while True:
            response = self.printerSerial.readline().decode().strip()
            if response == 'ok':
                break

    def elevateZ(self):
        if self.homed:
            self.printerSerial.write(b'G1 Z40 F1000\n')
            while True:
                response = self.printerSerial.readline().decode().strip()
                if response == 'ok':
                    break
        else:
            self.home()


    def middleXY(self):
        if self.homed:
            self.printerSerial.write(b'G1 Z30 X100 Y100 F10000\n')
            while True:
                response = self.printerSerial.readline().decode().strip()
                if response == 'ok':
                    break
        else:
            self.home()

    def getInfo(self):
        self.printerSerial.write(b'M105\n')
        while True:
            response = self.printerSerial.readline().decode().strip()
            if response == 'ok':
                break
            print(response)

    def getTemp(self):
        self.printerSerial.write(b'M105\n')
        while True:
            response = self.printerSerial.readline().decode().strip()
            if response == 'ok':
                break
          

            split_string = response.split()
            for item in split_string:
                if item.startswith("T:"):
                    T_value = item.replace("T:", "")
                    break
                    
        return T_value


    def beep(self, frequency, duration):
        self.printerSerial.write(('M300 S{} P{} V\n'.format(frequency, duration)).encode())
        while True:
            response = self.printerSerial.readline().decode().strip()
            if response == 'ok':
                break

    def goToCords(self, xy):
        if self.homed is not True:
            self.home()
        x, y = xy
        cmd = f"G1 F1500 X{x} Y{y}\n" + "G4 P10\n"
        self.printerSerial.write(cmd.encode())
    
    def stop_print(self):
        self.printerSerial.write(b'M112\n')

    def get_z(self, json_dict, middle_point, image, tof):
        if not self.homed:
            self.home()
            sleep = 25
        else:
            sleep = 5
        
        samples = 10
        distance1 = 0
        distance2 = 0
        
        command = 'G1 X20 Y180 Z30 F2500\n'
        self.printerSerial.write(command.encode())
        while True:
            response = self.printerSerial.readline().decode().strip()
            if response == 'ok':
                break
                
        time.sleep(sleep)
            
        for count in range(0,samples + 1):
            distance = tof.get_distance()
            if distance > 0:
                distance1 += distance
            
            time.sleep(0.02)
        
        time.sleep(1)
        
        #Kod z GCODE.py, pro prevedni z pixelu na gcode
        printer_x_length_mm = 215  
        printer_y_length_mm = 200  
        width = json_dict['top_right'][0] - json_dict['top_left'][0]
        height = json_dict['bottom_left'][1] - json_dict['top_left'][1]
        image_height_pixels, image_width_pixels, _ = image.shape
        x_scale = printer_x_length_mm / width 
        y_scale = printer_y_length_mm / height  
        middle_x_pixel = image_width_pixels // 2
        x_pixel_mirror = middle_x_pixel - (middle_point[0] - middle_x_pixel)
        x_mm = round(((x_pixel_mirror * x_scale) + 0), 2)
        y_mm = round((middle_point[1] * y_scale) - 6, 2)
        
        command = 'G1 X%d Y%d Z30 F2500\n' % (x_mm - 21, y_mm + 1)
        self.printerSerial.write(command.encode())
        while True:
            response = self.printerSerial.readline().decode().strip()
            if response == 'ok':
                break
        
        time.sleep(5)
        
        for count in range(0,samples + 1):
            distance = tof.get_distance()
            if distance > 0:
                distance2 += distance
            
            time.sleep(0.02)
        
        distance1 = distance1/samples
        distance2 = distance2/samples
        vysledek = round((distance2 - distance1), 1)
        printer_in = round(((vysledek * 2) + 0)/10, 1)
        
        self.printerSerial.write(b'G1 X0 Y210 Z10 F1000\n')
        while True:
            response = self.printerSerial.readline().decode().strip()
            if response == 'ok':
                break
        
        return printer_in
    
    def shake(self):
        if self.homed:
            gcode_list = ["G1 Z0 F1000", "P1500", "G1 Y170 F1500", "G1 Y210 F1500", "G1 Y170 F1500", "G1 Y210 F1500", "G1 Z10 F1000"]
            for line in gcode_list:
                try:
                    self.printerSerial.write((line + '\n').encode())
                    while True:
                        response = self.printerSerial.readline().decode().strip()
                        if response == 'ok':
                            break
                except:
                    pass
        else:
            self.home()
        
        
    
    def write_gcodelist(self, gcode_list):
        if not self.homed:
            self.home()
        for line in gcode_list:
            try:
                self.printerSerial.write((line + '\n').encode())
                while True:
                    response = self.printerSerial.readline().decode().strip()
                    if response == 'ok':
                        break
            except:
                return True

        
        return True
                        
            



