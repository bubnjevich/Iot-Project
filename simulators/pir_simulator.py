import random
import threading
import time


class MotionSensorSimulator(threading.Thread):
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
                self.callback(1 if motion == 'Detected' else 0, self.settings, self.publish_event)
                time.sleep(5)