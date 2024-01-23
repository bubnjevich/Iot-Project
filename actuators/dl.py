from collections.abc import Callable, Iterable, Mapping
import threading
import time
from typing import Any
import paho.mqtt.client as mqtt
import time
from broker_settings import HOSTNAME
try:
	import RPi.GPIO as GPIO
except:
	pass


class LED(threading.Thread):
    def __init__(self, port, output_queue, callback, settings, publish_event): # port 18
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = False
        self.port = port
        self.state = False
        self.settings = settings
        self.callback = callback
        self.publish_event = publish_event
    
    def setup(self):
        #GPIO.setmode(GPIO.BCM)
        #GPIO.setup(self.port,GPIO.OUT)
        pass

    def toggle_light(self):
        self.state = True
        time.sleep(10)
        self.state = False

    def on_connect(self, client, userdata, flags, rc):
        # Subscribe to the topic on successful connection
        client.subscribe("LIGHT_" + self.settings["runs_on"])

 
    def run(self):
        self.setup()
        mqtt_client = mqtt.Client()
        mqtt_client.connect(HOSTNAME, 9001, 60)
        mqtt_client.loop_start()
        mqtt_client.on_connect = self.on_connect
        mqtt_client.on_message = lambda client, userdata, message: self.toggle_light()
        while True:
            if self.running_flag:
                state = 1
                if not self.state:
                     state = 0
                self.callback(state, self.settings, self.publish_event)
                #self.output_queue.put(f"Current Door Light State: {state}")
                if self.state:
                    #GPIO.output(self.port,GPIO.HIGH)
                    print("RADIIIIIIIIIIIIIIIIIIIIIIIIIIII")
                    pass
                else:
                    #GPIO.output(self.port,GPIO.LOW)
                    pass
                time.sleep(1)

       