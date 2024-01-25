import random
import threading
import time
import paho.mqtt.client as mqtt
from broker_settings import HOSTNAME, SERVER_IP
from datetime import datetime

import json
class MotionSensorSimulator(threading.Thread): # PIR 1, PIR2, RPIR 1 - 4
    def __init__(self, output_queue, callback, settings, publish_event):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = True
        self.callback = callback
        self.settings = settings
        self.publish_event = publish_event
        self.last_distances = [200.]
        self.current_number = 0     # inicjalno nikog nema u objektu
        self.mqtt_client = mqtt.Client()
        self.mqtt_server = mqtt.Client()


    def save_last_distances(self, distance):

        if len(self.last_distances) == 2:
            self.last_distances.pop(0)
        self.last_distances.append(distance)


    def on_connect(self, client, userdata, flags, rc):
        # Subscribe to the topic on successful connection
        if self.settings["name"] == "DB - MY_DPIR1":
            client.subscribe("DUS1")
        elif self.settings["name"] == "Door Motion Sensor 2":
            client.subscribe("DUS2")


    def save_current_people_count(self):
        if len(self.last_distances) == 2:

            current_timestamp = datetime.utcnow().isoformat()

            status_payload = {
                "measurement": "NumberPeople",
                "name": self.settings["name"],
                "time" : current_timestamp,
                "value": -1
            }
            if self.last_distances[1] - self.last_distances[0] > 0:  # osoba izlazi iz objekta
                status_payload["value"] = 1
            self.mqtt_server.publish("CurrentPeopleNumber", json.dumps(status_payload)) # salji na server


    def run(self):
        self.mqtt_client.connect(HOSTNAME, 1883, 60)
        self.mqtt_client.loop_start()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = lambda client, userdata, message: self.save_last_distances(float(message.payload.decode()))


        self.mqtt_server.connect(SERVER_IP, 1883, 60)
        self.mqtt_server.loop_start()

        while True:
            if self.running_flag:
                motion = random.choice(['Detected', 'Not Detected'])
                if motion == 'Detected':
                    if self.settings["name"] == "DB - MY_DPIR1":
                        self.mqtt_client.publish("LIGHT_" + self.settings["runs_on"], motion)
                        self.save_current_people_count()
                    elif self.settings["name"] == "Door Motion Sensor 2":
                        self.save_current_people_count()
                    elif self.settings["name"] in ["DB - SMART_RPIR1", "DB - SMART RPIR2", "Room PIR 3", "Room PIR 4"]:
                        current_timestamp = datetime.utcnow().isoformat()
                        status_payload = {
                            "measurement": "Motion",
                            "start": 1,
                            "device_name": self.settings["name"],
                            "time": current_timestamp,
                            "type" : self.settings["name"]

                        }
                        self.mqtt_server.publish("RPIR", json.dumps(status_payload))
                self.output_queue.put("Detected" if motion == "Detected" else "Not Detected")
                self.callback(1 if motion == 'Detected' else 0, self.settings, self.publish_event)
                time.sleep(5)