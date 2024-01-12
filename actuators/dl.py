from collections.abc import Callable, Iterable, Mapping
import threading
import time
from typing import Any
try:
	import RPi.GPIO as GPIO
except:
	pass


class LED(threading.Thread):
    def __init__(self, port, output_queue): # port 18
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
                state = "ON"
                if not self.state:
                     state = "OFF"
                self.output_queue.put(f"Current Door Light State: {state}")
                if self.state:
                    GPIO.output(self.port,GPIO.HIGH)
                else:
                    GPIO.output(self.port,GPIO.LOW)
                time.sleep(1)
