import random
import threading
import time


class DoorSensorSimulator(threading.Thread):
    def __init__(self, output_queue, callback, settings, publish_event):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = False
        self.callback = callback
        self.settings = settings
        self.publish_event = publish_event

    def run(self):
        while True:
            if self.running_flag:
                status = random.choice(['Unlocked', 'Locked'])
                self.callback(1 if status == 'Unlocked' else 0, self.settings, self.publish_event)
                self.output_queue.put(f"Door Sensor Status: {status}")
                time.sleep(1)
