import random
import threading
import time


class DoorBuzzerSimulator(threading.Thread):
    def __init__(self, output_queue):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = False

    def run(self):
        while True:
            if self.running_flag:
                    self.output_queue.put("Buzz")
                    time.sleep(0.1)
                    self.output_queue.put("Buzz")
                    time.sleep(0.1)
                    self.output_queue.put("Buzz")
                    time.sleep(5)