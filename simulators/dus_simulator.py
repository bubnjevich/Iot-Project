
import random
import threading
import time
import paho.mqtt.client as mqtt
from broker_settings import HOSTNAME


class DoorUltrasonicSensorSimulator(threading.Thread):
    def __init__(self, output_queue, callback, settings, publish_event):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = True
        self.callback = callback
        self.settings = settings
        self.publish_event = publish_event

    def run(self):
        mqtt_client = mqtt.Client()
        mqtt_client.connect(HOSTNAME, 1883, 60)
        mqtt_client.loop_start()
        while True:
            if self.running_flag:
                distance = round(random.uniform(1, 100), 2)
                # print("SALJEM DISTANCU: ", distance, "  sa ", self.settings["name"])
                if self.settings["name"] == "DUS1 - Device DUS":
                   mqtt_client.publish("DUS1", distance)
                elif self.settings["name"] == "Door Ultrasonic Sensor 2":
                    mqtt_client.publish("DUS2", distance)
                self.callback(distance, self.settings, self.publish_event)
                time.sleep(4)