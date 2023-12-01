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
        
        self.printerSerial.write(b'G1 X0 Y210 F1000\n')
        while True:
            response = self.printerSerial.readline().decode().strip()
            if response == 'ok':
                break

    def elevateZ(self):
        if self.homed:
            self.printerSerial.write(b'G1 Z15 F1000\n')
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
                        
            



