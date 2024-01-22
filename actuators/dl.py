from collections.abc import Callable, Iterable, Mapping
import threading
import time
from typing import Any
try:
    import RPi.GPIO as GPIO
except:
    pass


class LED(threading.Thread):

    def __init__(self, port, output_queue, callback, settings, publish_event):  # port 18
        super().__init__(name='DoorLightThread')
        self.output_queue = output_queue
        self.running_flag = True
        self.port = port
        self.state = False  # inicijalno  ne pali lampicu
        self.settings = settings
        self.callback = callback
        self.publish_event = publish_event




    def setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.port, GPIO.OUT)
        pass

    def run(self):
        self.setup()
        while True:
            if self.running_flag:
                if self.state:
                    GPIO.output(self.port, GPIO.HIGH)
                    time.sleep(9)
                    self.state = False
                else:
                    GPIO.output(self.port, GPIO.LOW)
                time.sleep(1) # ukljuci dl na 10 sekundi



