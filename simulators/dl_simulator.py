import threading
import time

class DoorLightSimulator(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running_flag = False
        self.state = False

    def run(self):
        while True:
            if self.running_flag:
                print(f"Current Door Light State: {self.state}")
                time.sleep(5)
