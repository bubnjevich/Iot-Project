
import random
import threading
import time
import paho.mqtt.client as mqtt
from broker_settings import PI3


class IRSimulator(threading.Thread):
    def __init__(self, output_queue, callback, settings, publish_event):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = True
        self.callback = callback
        self.settings = settings
        self.publish_event = publish_event
        self.buttons_names = ["LEFT",   "RIGHT",      "UP",       "DOWN",       "2",          "3",          "1",        "OK",        "4",         "5",         "6",         "7",         "8",          "9",        "*",         "0",        "#"]  # String list in same order as HEX list



    def run(self):
        mqtt_client = mqtt.Client()
        mqtt_client.connect("localhost", 1883, 60)
        mqtt_client.loop_start()
        button_to_color = {
            "1": "off",
            "2": "white",
            "3": "red",
            "4": "green",
            "5": "blue",
            "6": "yellow",
            "7": "purple",
            "8": "light_blue",
        }
        while True:
            if self.running_flag:
                simulated_button = random.choice(self.buttons_names)
                self.callback(simulated_button, self.settings, self.publish_event)
                try:
                    color = button_to_color.get(simulated_button, "")     
                    mqtt_client.publish("LightChange", color)
                except:
                    pass
                time.sleep(4)