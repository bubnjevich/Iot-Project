import random
import threading
import time
import paho.mqtt.client as mqtt
from datetime import datetime

import json
class MotionSensorSimulator(threading.Thread): # PIR 1, PIR2, RPIR 1 - 4
    def __init__(self, output_queue, callback, settings, publish_event):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = True
        self.callback = callback
        self.settings = settings
        self.publish_event = publish_event

    def run(self):
        while True:
            if self.running_flag:
                motion = random.choice(['Detected', 'Not Detected'])
                if motion == 'Detected':
                    self.output_queue.put("Detected" if motion == "Detected" else "Not Detected")
                self.callback(1 if motion == 'Detected' else 0, self.settings, self.publish_event)
                time.sleep(30) # 30