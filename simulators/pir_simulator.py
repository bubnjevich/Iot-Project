import random
import threading
import time


class MotionSensorSimulator(threading.Thread):
    def __init__(self, output_queue):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = False

    def run(self):
        while True:
            if self.running_flag:
                motion = random.choice(['Detected', 'Not Detected'])
                self.output_queue.put(f"Motion Sensor Status: {motion}")
                time.sleep(1)