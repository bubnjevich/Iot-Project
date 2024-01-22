
import random
import threading
import time


class DoorUltrasonicSensorSimulator(threading.Thread):
    def __init__(self, output_queue, callback, settings, publish_event):
        super().__init__(name=settings["name"])
        self.output_queue = output_queue
        self.running_flag = True
        self.callback = callback
        self.settings = settings
        self.publish_event = publish_event
        self.last_distances  = [120.]     # inicijalno 120

    def run(self):
        while True:
            if self.running_flag:
                distance = round(random.uniform(20, 140), 2)
                if len(self.last_distances) == 2:
                    self.last_distances.pop(0) # ukloni prvi element jer nam vise ne treba za proveru da li osoba ulazi ili izlazi
                self.last_distances.append(distance)
                self.callback(distance, self.settings, self.publish_event)
                time.sleep(1)