import threading
import time
import random
from datetime import datetime
import paho.mqtt.client as mqtt
import json
from broker_settings import HOSTNAME

class DoorMembraneSwitchSimulator(threading.Thread):
    def __init__(self, output_queue, callback, settings, publish_event):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = True
        self.callback = callback
        self.settings = settings
        self.publish_event = publish_event


    def send_dms(self, mqtt_client, digits):
        print("SALJEM DMS: ", digits)
        current_timestamp = datetime.utcnow().isoformat()
        status_payload = {
            "measurement": "DMS",
            "device_name" : self.settings["name"],
            "value" : digits,
            "time" : current_timestamp
        }

        mqtt_client.publish("DMS", json.dumps(status_payload))

    def run(self):
        mqtt_client = mqtt.Client()
        mqtt_client.connect(HOSTNAME, 1883, 60)
        mqtt_client.loop_start()
        while True:
            l = ""
            for value in generate_value(): # salji input od 4 digit-a
                l += value
                if self.running_flag and len(l) == 4:
                    self.send_dms(mqtt_client, "1234")
                    self.callback(l, self.settings, self.publish_event)
                    l = ""
                    time.sleep(50)

def generate_value():
      while True:
            value = random.choice(['A', 'B', 'C', 'D', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '*', '#'])
            yield  value