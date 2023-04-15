import serial, time
import math

def move_to_circle(n_points, center_x, center_y, radius, speed):
    gcode = []
    for i in range(n_points):
        angle = 2 * math.pi * i / n_points
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        gcode.append("G1 X{} Y{} F{}".format(round(x, 3), round(y, 3), speed))

    return gcode

def move_to_heart(n_points, center_x, center_y, speed, size):
    gcode = []
    for i in range(n_points):
        angle = 2 * math.pi * i / n_points
        x = center_x + size*(16 * math.pow(math.sin(angle), 3))
        y = center_y + size*(13 * math.cos(angle) - 5 * math.cos(2*angle) - 2 * math.cos(3*angle) - math.cos(4*angle))
        gcode.append("G1 X{} Y{} F{}".format(round(x, 3), round(y, 3), speed))
    return gcode

class Printer():

    def __init__(self,COM, bedSize):
        self.COM = COM
        self.max_X, self.max_Y = bedSize
        self.position = (0,0)
        self.homed = False
        try:
            self.printerSerial = serial.Serial(COM,115200, timeout=25)
        except:
            print("Connection error")

    def WritePoints(self, xy):
        x,y = xy
        x = self.max_X - x
        self.position = xy

        command = 'G1 F500 X%d Y%d\n' % (x, y) + 'G4 P1000\n' + 'G1 F500 X0 Y0\n'

        print(command.encode())

        if self.printerSerial is not None:
            self.printerSerial.write(command.encode())
            return 1
        else:
            return 0

    def home(self):
        self.printerSerial.write(b'G28\n')
        while True:
            response = self.printerSerial.readline().decode().strip()
            if response == 'ok':
                break

        self.homed = True

    def elevateZ(self):
        if self.homed is True:
            self.printerSerial.write(b'G1 Z15 F1000\n')
            while True:
                response = self.printerSerial.readline().decode().strip()
                if response == 'ok':
                    break
        else:
            self.home()


    def middleXY(self):
        if self.homed is True:
            self.printerSerial.write(b'G1 Z30 X100 Y100 F10000\n')
            while True:
                response = self.printerSerial.readline().decode().strip()
                if response == 'ok':
                    break
        else:
            self.home()

    def getInfo(self):
        self.printerSerial.write(b'M115 V\n')
        while True:
            response = self.printerSerial.readline().decode().strip()
            if response == 'ok':
                break
            print(response)

    def getTemp(self):
        self.printerSerial.write(b'M105 T\n')
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
        x, y = xy
        cmd = f"G1 F5000 X{x} Y{y}\n" + "G4 P10\n"
        self.printerSerial.write(cmd.encode())

    def write_gcodelist(self, gcode_list):
        if self.homed is not True:
            self.home()
        else:
            for line in gcode_list:
                self.printerSerial.write((line + '\n').encode())
                while True:
                    response = self.printerSerial.readline().decode().strip()
                    if response == 'ok':
                        break
            self.middleXY()


