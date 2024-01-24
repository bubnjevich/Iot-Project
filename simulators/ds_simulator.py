import random
import threading
import time
from datetime import datetime
import paho.mqtt.client as mqtt
from broker_settings import HOSTNAME, SERVER_IP
import json

class DoorSensorSimulator(threading.Thread):
    def __init__(self, output_queue, callback, settings, publish_event):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = True
        self.alarm_system_active = True  # sistem alarma inicijalno upaljen
        self.callback = callback
        self.settings = settings
        self.publish_event = publish_event
        self.locked_counter = 0

    def stop_alarm(self, mqtt_client):
        current_timestamp = datetime.utcnow().isoformat()
        status_payload = {
            "measurement": "Alarm",
            "alarm_name": "Door Alarm " + self.settings["runs_on"],
            "device_name": self.settings["name"],
            "type": "DS" + self.settings["runs_on"],
            "start": 0,
            "time": current_timestamp
        }

        mqtt_client.publish("Alarm", json.dumps(status_payload))
        pass

    def start_alarm(self, mqtt_client):
        print("saljem na server....")
        current_timestamp = datetime.utcnow().isoformat()
        status_payload = {
            "measurement": "Alarm",
            "alarm_name": "Door Alarm " + self.settings["runs_on"],
            "device_name" : self.settings["name"],
            "type": "DS" + self.settings["runs_on"],
            "start" : 1,
            "time" : current_timestamp
        }

        mqtt_client.publish("Alarm", json.dumps(status_payload))

    def run(self):
        mqtt_client = mqtt.Client()
        mqtt_client.connect(SERVER_IP, 1883, 60)
        mqtt_client.loop_start()
        while True:
            if self.running_flag:
                import random
                status = random.choice((1, 0))  # 1 = "Unlocked", 0 = "Locked"
                if status: # status == 1
                    self.locked_counter += 1
                    if self.locked_counter == 2:
                        self.start_alarm(mqtt_client)
                else:
                    if self.locked_counter >= 2:
                        self.stop_alarm(mqtt_client)
                    self.locked_counter = 0
                self.callback(status, self.settings, self.publish_event)
                time.sleep(2)
