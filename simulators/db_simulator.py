import random
import threading
import time
import paho.mqtt.client as mqtt
from broker_settings import SERVER_IP
import json


class DoorBuzzerSimulator(threading.Thread):
    def __init__(self, output_queue, callback, settings, publish_event):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = False
        self.system_active = False # inicijalno sistem alarma je ugasen, pali se preko DMS-a
        self.callback = callback
        self.settings = settings
        self.publish_event = publish_event
        self.alarm_list = []
        self.pin = ""

    def handle_alarm(self, data, mqtt_client):
        if data["measurement"] == "Clock":
            # Proverite da li treba da se upali budilnik
            if data["value"]:
                # print("AKTIVIRAN BUDILNIK: BUZZ BUZZ BUZZ BUZZZ!!!!!")
                self.running_flag = True
            else:
                # Isključite budilnik
                # print("BUDILNIK UGASEN")
                self.running_flag = False
        
        if data["measurement"] == "DMS":
            if self.pin == "" and  not data["simulated"]: # ako korisnik prvi put unosi DMS
                print("postavio self.pin na ", data["value"])
                self.pin = data["value"]
                time.sleep(10)
                self.system_active = True
            else:
                if data["value"] == self.pin:
                    if self.running_flag:   # ako je upaljen alarm
                        print("Alarm/i je bio upaljen SVE gasim...")
                        self.running_flag = False
                        self.system_active = False
                        self.alarm_list = []
                    
                    elif not self.system_active: # nije sistem aktivan
                        print("Sistem nije bio aktivan. Aktiviracu sistem alarma za 10 sekundi.....")
                        time.sleep(10)  # aktiviraj nakon 10 sekundi
                        self.system_active = True
            return

        if self.system_active:
            if data["start"]: # ako je aktivan sistem i treba da se upali alarm
                # print("Sistem je aktivan i palim alarm zbor promene DS-a")
                self.running_flag = True
                self.alarm_list.append(data["type"])
                # print("Current: ", self.alarm_list)

            if not data["start"]:
                # print("Gasim jedan od alarma...")
                if len(self.alarm_list) != 0:
                    self.alarm_list.remove(data["type"])
                    # print("Current: ", self.alarm_list)
                if len(self.alarm_list) == 0:
                    # print("Gasim alarme jer ih vise nema...")
                    self.running_flag = False
            data["measurement"] = "NotifyFrontend"
            mqtt_client.publish("NotifyFrontend", json.dumps(data))
    
    def run(self):
        mqtt_client = mqtt.Client()
        mqtt_client.connect(SERVER_IP, 1883, 60)
        mqtt_client.loop_start()
        mqtt_client.subscribe("AlarmAlerted") # info from server
        if self.settings["name"] == "Bedroom Buzzer":
            mqtt_client.subscribe("Clock")

        mqtt_client.on_message = lambda client, userdata, message: self.handle_alarm(json.loads(message.payload.decode('utf-8')), mqtt_client)
        while True:
            if self.running_flag:
                self.callback(1, self.settings, self.publish_event)
                time.sleep(0.1)
                self.callback(1, self.settings, self.publish_event)
                time.sleep(0.1)
                self.callback(1, self.settings, self.publish_event)
                self.output_queue.put("Buzz buzz buzz")
