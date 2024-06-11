import threading
import time

class FourSegmentSimulator(threading.Thread):

    def __init__(self, output):
        super().__init__()
        self.output = output

    def run(self) -> None:
        while True:
            current_time = time.strftime("%H:%M")
            self.output.put(current_time)
            time.sleep(5)