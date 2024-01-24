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
        self.last_distances = [200.]
        self.current_number = 0     # inicjalno nikog nema u objektu


    def save_people_count(self, distance):
        if len(self.last_distances) == 2:
            self.last_distances.pop(0)
        self.last_distances.append(distance)
        #print("Primljeno  ", distance, " na" , self.settings["name"])
        if self.last_distances[1] - self.last_distances[0] > 0:  # osoba izlazi iz objekta
            self.current_number = max(0, self.current_number - 1)
            #print("Osoba izasla iz objekta. Broj ljudi : ", self.current_number)
        else:
            self.current_number += 1
            #print("Osoba usla u objekat. Broj ljudi : ", self.current_number)


    def on_connect(self, client, userdata, flags, rc):
        # Subscribe to the topic on successful connection
        if self.settings["name"] == "DB - MY_DPIR1":
            client.subscribe("DUS1")
        elif self.settings["name"] == "Door Motion Sensor 2":
            client.subscribe("DUS2")


    def run(self):
        mqtt_client = mqtt.Client()
        mqtt_client.connect(HOSTNAME, 1883, 60)
        mqtt_client.loop_start()
        mqtt_client.on_connect = self.on_connect
        mqtt_client.on_message = lambda client, userdata, message: self.save_people_count(float(message.payload.decode()))
        while True:
            if self.running_flag:
                motion = random.choice(['Detected', 'Not Detected'])
                if motion == "Detected" and (self.settings["name"] == "DB - MY_DPIR1" or self.settings["name"] == "Door Motion Sensor 2"):
                    mqtt_client.publish("LIGHT_" + self.settings["runs_on"], motion)
                self.callback(1 if motion == 'Detected' else 0, self.settings, self.publish_event)
                time.sleep(5)