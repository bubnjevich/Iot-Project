import random
import threading
import time


class DoorSensorSimulator(threading.Thread):
    def __init__(self, output_queue):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = False

    def run(self):
        while True:
            if self.running_flag:
                status = random.choice(['Unlocked', 'Locked'])
                self.output_queue.put(f"Door Sensor Status: {status}")
                time.sleep(1)
