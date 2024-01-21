import threading
import time

class DoorLightSimulator(threading.Thread):
    def __init__(self, output_queue, callback, settings, publish_event):
        super().__init__()
        self.running_flag = True
        self.state = False
        self.output_queue = output_queue
        self.callback = callback
        self.settings = settings
        self.publish_event = publish_event

    def run(self):
        while True:
            if self.running_flag:
                state = 1
                if not self.state:
                     state = 0
                self.output_queue.put(f"Current Door Light State: {state}")
                #self.callback(state, self.settings, self.publish_event)
                time.sleep(5)
