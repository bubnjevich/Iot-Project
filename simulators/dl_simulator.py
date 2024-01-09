import threading
import time

class DoorLightSimulator(threading.Thread):
    def __init__(self, output_queue):
        super().__init__()
        self.running_flag = True
        self.state = False
        self.output_queue = output_queue

    def run(self):
        while True:
            if self.running_flag:
                state = "ON"
                if not self.state:
                     state = "OFF"
                self.output_queue.put(f"Current Door Light State: {state}")
                time.sleep(5)
