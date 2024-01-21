import threading
import time
import random

class DoorMembraneSwitchSimulator(threading.Thread):
    def __init__(self, output_queue, callback, settings, publish_event):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = True
        self.callback = callback
        self.settings = settings
        self.publish_event = publish_event

    def run(self):
        while True:
            l = ""
            for value in generate_value(): # salji input od 4 digit-a
                l += value
                if self.running_flag and len(l) == 4:
                    self.callback(l, self.settings, self.publish_event)
                    l = ""
                    time.sleep(1)

def generate_value():
      while True:
            value = random.choice(['A', 'B', 'C', 'D', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '*', '#'])
            yield  value