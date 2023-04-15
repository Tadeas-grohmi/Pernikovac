import RPi.GPIO as GPIO
import time

class RpiGPIO():
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        #pin 12 na LEDky pwm
        GPIO.setup(12, GPIO.OUT)  
        self.pwm = GPIO.PWM(12, 100)
        self.pwm.start(0)
    
    def led_brightness(self, brightness):
        self.pwm.ChangeDutyCycle(brightness)
    
    def stop_gpio(self):                      
        GPIO.cleanup()
        
    def detect_push(self, button_pin):
        GPIO.setup(button_pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        button_pred = 1
        is_held = False
        print("Waiting for button")
        while True:
            button_state = GPIO.input(button_pin)
            if button_state != button_pred and not is_held:
                print("Button pressed")
                is_held = True
                return True
            
            if button_state == 1 and button_pred == 0:
                    is_held = False
            
            button_pred = button_state
            time.sleep(0.01)
    





