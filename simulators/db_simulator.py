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
        self.system_active = True
        self.callback = callback
        self.settings = settings
        self.publish_event = publish_event
        self.alarm_list = []
        self.pin = "1234"

    def handle_alarm(self, data):

        if data["measurement"] == "DMS":
            # print("PRIMELJEN DMS: ", data["value"])
            if data["value"] == self.pin:
                if self.running_flag:   # ako je upaljen alarm
                    # print("Alarm je bio upaljen SVE gasim...")
                    self.running_flag = False
                    self.system_active = False
                    self.alarm_list = []
                elif not self.system_active: # nije sistem aktivan
                    # print("Aktiviracu sistem alarma za 10 sekundi.....")
                    time.sleep(10)  # aktiviraj nakon 10 sekundi
                    self.system_active = True
                elif self.system_active:
                    # print("Deaktiviram sistem i sve alarme....")
                    self.system_active = False
                    self.alarm_list = []
            return

        if self.system_active:
            if data["start"]: # ako je aktivan sistem i treba da se upali alarm
                #print("Sistem je aktivan i palim alarm zbor promene DS-a")
                self.running_flag = True
                self.alarm_list.append(data["type"])

            if not data["start"]:
                #print("Gasim jedan od alarma...")
                if len(self.alarm_list) != 0 and data["type"] in self.alarm_list:

                    self.alarm_list.remove(data["type"])
                elif len(self.alarm_list) != 0 and not data["type"] in self.alarm_list:
                    self.alarm_list.pop()
                if len(self.alarm_list) == 0:
                    #print("Gasim alarme jer ih vise nema...")
                    self.running_flag = False

    def run(self):
        mqtt_client = mqtt.Client()
        mqtt_client.connect(HOSTNAME, 1883, 60)
        mqtt_client.loop_start()
        mqtt_client.subscribe("AlarmAlerted")


        mqtt_client.on_message = lambda client, userdata, message: self.handle_alarm(json.loads(message.payload.decode('utf-8')))
        while True:
            if self.running_flag:
                self.callback(1, self.settings, self.publish_event)
                time.sleep(0.1)
                self.callback(1, self.settings, self.publish_event)
                time.sleep(0.1)
                self.callback(1, self.settings, self.publish_event)
                self.output_queue.put("Buzz buzz buzz")
