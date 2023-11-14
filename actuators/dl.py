from collections.abc import Callable, Iterable, Mapping
import threading
import time
from typing import Any
try:
	import RPi.GPIO as GPIO
except:
	pass


class LED(threading.Thread):
    def __init__(self, port, output_queue):
        self.output_queue = output_queue
        self.running_flag = False
        self.port = port
        self.state = False
    
    def setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.port,GPIO.OUT)
        
    def run(self):
        self.setup()
        while True:
            if self.running_flag:
                print(f"Current Door Light State: {self.state}")
                new_state = input("Enter New Door Light State (on/off): ")
                if(new_state.upper() == "ON"):
                    self.state = True
                    GPIO.output(self.port,GPIO.HIGH)
                elif(new_state.upper() == "OFF"):
                    self.start = False
                    GPIO.output(self.port,GPIO.LOW)
                time.sleep(1)
