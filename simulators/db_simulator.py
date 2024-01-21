import random
import threading
import time


class DoorBuzzerSimulator(threading.Thread):
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
                    #self.output_queue.put("Buzz")
                    self.callback(1, self.settings, self.publish_event)
                    time.sleep(0.1)
                    self.callback(1, self.settings, self.publish_event)
                    time.sleep(0.1)
                    self.callback(1, self.settings, self.publish_event)
