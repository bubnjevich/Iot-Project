import random
import threading
import time
import paho.mqtt.client as mqtt
from broker_settings import HOSTNAME


class MotionSensorSimulator(threading.Thread):
    def __init__(self, output_queue, callback, settings, publish_event):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = True
        self.callback = callback
        self.settings = settings
        self.publish_event = publish_event

    def run(self):
        mqtt_client = mqtt.Client()
        mqtt_client.connect(HOSTNAME, 9001, 60)
        mqtt_client.loop_start()
        while True:
            if self.running_flag:
                motion = random.choice(['Detected', 'Not Detected'])
                if(motion == "Detected" and (self.settings["name"] == "DB - MY_DPIR1" or self.settings["name"] == "Door Motion Sensor 2")):
                    print("POMERIO SEEE")
                    mqtt_client.publish("LIGHT_" + self.settings["runs_on"], motion)
                self.callback(1 if motion == 'Detected' else 0, self.settings, self.publish_event)
                time.sleep(5)