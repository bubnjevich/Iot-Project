import threading
import time
import random




class GSGSimulator(threading.Thread):
    def __init__(self, output_queue, callback, settings, publish_event):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = True
        self.callback = callback
        self.settings = settings
        self.publish_event = publish_event

    def run(self):
        while True:
            # TODO: videti znacajan pomeraj
            accel = [random.random() / 4, random.random() / 4, 9.81 + random.random() / 4]
            gyro = [random.random() * 3.0, random.random() * 3.0, random.random() * 3.0]
            if self.running_flag:
                self.callback(accel, gyro, self.settings, self.publish_event)
            time.sleep(1) # 0.1