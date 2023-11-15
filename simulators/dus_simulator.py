
import random
import threading
import time


class DoorUltrasonicSensorSimulator(threading.Thread):
    def __init__(self, output_queue):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = False

    def run(self):
        while True:
            if self.running_flag:
                distance = round(random.uniform(1, 100), 2)
                self.output_queue.put(f"Distance: {distance} cm")
                time.sleep(1)