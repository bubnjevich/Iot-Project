import random
import threading
import time
import paho.mqtt.client as mqtt
from broker_settings import HOSTNAME
import json


class DoorBuzzerSimulator(threading.Thread):
    def __init__(self, output_queue, callback, settings, publish_event):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = False
        self.callback = callback
        self.settings = settings
        self.publish_event = publish_event
        self.alarm_list = []

    def handle_alarm(self, data):
        if data["start"]:
            self.running_flag = True
            self.alarm_list.append(data["type"])
        else:
            self.alarm_list.remove(data["type"])
            if len(self.alarm_list) == 0:
                self.running_flag = False    

    def run(self):
        mqtt_client = mqtt.Client()
        mqtt_client.connect(HOSTNAME, 1883, 60)
        mqtt_client.loop_start()
        mqtt_client.subscribe("Alarm")
        mqtt_client.on_message = lambda client, userdata, message: self.handle_alarm(json.loads(message.payload.decode('utf-8')))
        while True:
            if self.running_flag:
                print("Buzz buzz buzz...")
                self.callback(1, self.settings, self.publish_event)
                time.sleep(0.1)
                self.callback(1, self.settings, self.publish_event)
                time.sleep(0.1)
                self.callback(1, self.settings, self.publish_event)
