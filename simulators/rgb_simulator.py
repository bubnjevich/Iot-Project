
import random
import threading
import time
import paho.mqtt.client as mqtt
from broker_settings import HOSTNAME


class RGBimulator(threading.Thread):
    def __init__(self, output_queue, callback, settings, publish_event):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = True
        self.callback = callback
        self.color = ""
        self.settings = settings
        self.publish_event = publish_event
        self.color_names = ["off", "white", "red", "blue", "green", "yellow", "purple", "light_blue"]

    def change_lights(self, lient, userdata, message):
        color = message.payload.decode()
        self.color= color
        self.callback(self.color, self.settings, self.publish_event)

        

    def run(self):
        mqtt_client = mqtt.Client()
        mqtt_client.connect("localhost", 1883, 60)
        mqtt_client.loop_start()
        mqtt_client.on_connect = lambda client, userdata, flags, rc: client.subscribe("LightChange")
        mqtt_client.on_message = self.change_lights
        while True:
            if self.running_flag:
                selected_color = random.choice(self.color_names)
                self.color = selected_color
                self.callback(self.color, self.settings, self.publish_event)
                time.sleep(4)