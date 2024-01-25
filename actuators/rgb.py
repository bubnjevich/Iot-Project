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

class RGBLED(threading.Thread):
    def __init__(self, output_queue, callback, settings, publish_event): # port 18
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = True
        self.red_pin = settings["red_pin"]
        self.green_pin = settings["green_pin"]
        self.blue_pin = settings["blue_pin"]
        self.state = "off"
        self.settings = settings
        self.callback = callback
        self.publish_event = publish_event

    def setup(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.red_pin, GPIO.OUT)
        GPIO.setup(self.green_pin, GPIO.OUT)
        GPIO.setup(self.blue_pin, GPIO.OUT)

    def turnOff(self):
        self.state = "off"
        GPIO.output(self.red_pin, GPIO.LOW)
        GPIO.output(self.green_pin, GPIO.LOW)
        GPIO.output(self.blue_pin, GPIO.LOW)
        
    def white(self):
        self.state = "white"
        GPIO.output(self.red_pin, GPIO.HIGH)
        GPIO.output(self.green_pin, GPIO.HIGH)
        GPIO.output(self.blue_pin, GPIO.HIGH)
        
    def red(self):
        self.state = "red"
        GPIO.output(self.red_pin, GPIO.HIGH)
        GPIO.output(self.green_pin, GPIO.LOW)
        GPIO.output(self.blue_pin, GPIO.LOW)

    def green(self):
        self.state = "green"
        GPIO.output(self.red_pin, GPIO.LOW)
        GPIO.output(self.green_pin, GPIO.HIGH)
        GPIO.output(self.blue_pin, GPIO.LOW)
        
    def blue(self):
        self.state = "blue"
        GPIO.output(self.red_pin, GPIO.LOW)
        GPIO.output(self.green_pin, GPIO.LOW)
        GPIO.output(self.blue_pin, GPIO.HIGH)
        
    def yellow(self):
        self.state = "yellow"
        GPIO.output(self.red_pin, GPIO.HIGH)
        GPIO.output(self.green_pin, GPIO.HIGH)
        GPIO.output(self.blue_pin, GPIO.LOW)
        
    def purple(self):
        self.state = "purple"
        GPIO.output(self.red_pin, GPIO.HIGH)
        GPIO.output(self.green_pin, GPIO.LOW)
        GPIO.output(self.blue_pin, GPIO.HIGH)
        
    def light_blue(self):
        self.state = "light_blue"
        GPIO.output(self.red_pin, GPIO.LOW)
        GPIO.output(self.green_pin, GPIO.HIGH)
        GPIO.output(self.blue_pin, GPIO.HIGH)

    def change_lights(self, lient, userdata, message):
        color = message.payload.decode()
        color_function_map = {
            "white": self.white,
            "red": self.red,
            "green": self.green,
            "blue": self.blue,
            "yellow": self.yellow,
            "purple": self.purple,
            "light_blue": self.light_blue,
            "off": self.turnOff
        }
        function = color_function_map.get(color, None)
        if function:
            function()

    def run(self):
        self.setup()
        mqtt_client = mqtt.Client()
        mqtt_client.connect("localhost", 1883, 60)
        mqtt_client.loop_start()
        mqtt_client.on_connect = lambda client, userdata, flags, rc: client.subscribe("LightChange")
        mqtt_client.on_message = self.change_lights
        while True:
            if self.running_flag:
                self.callback(self.state, self.settings, self.publish_event)
                time.sleep(1)

