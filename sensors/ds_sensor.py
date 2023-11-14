import threading
import time
try:
	import RPi.GPIO as GPIO
except:
	pass

class Button(threading.Thread):
    def __init__(self, port, output_queue):
        self.port = port
        self.output_queue = output_queue
        self.running_flag = False

    
    def run(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.port, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.add_event_detect(self.port, GPIO.RISING, callback = self.button_pressed, bouncetime = 100)

    def button_pressed(self, event):
        if self.running_flag:
            self.output_queue.put("Door Sensor Status: unlocked")
    