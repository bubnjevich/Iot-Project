import time

from faust.serializers.codecs import json

try:
    import RPi.GPIO as GPIO
except:
    pass

from time import sleep
from broker_settings import SERVER_IP
import threading
import paho.mqtt.client as mqtt

#disable warnings (optional)

class RGBLed(threading.Thread):
    def __init__(self, callback, output, settings):
        super().__init__()
        self.RED_PIN = 12
        self.GREEN_PIN = 13
        self.BLUE_PIN = 19
        self.callback = callback
        self.output = output
        self.settings = settings
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.RED_PIN, GPIO.OUT)
        GPIO.setup(self.GREEN_PIN, GPIO.OUT)
        GPIO.setup(self.BLUE_PIN, GPIO.OUT)
        self.button = ""
    
    def turnOff(self):
        GPIO.output(self.RED_PIN, GPIO.LOW)
        GPIO.output(self.GREEN_PIN, GPIO.LOW)
        GPIO.output(self.BLUE_PIN, GPIO.LOW)
        
    def white(self):
        GPIO.output(self.RED_PIN, GPIO.HIGH)
        GPIO.output(self.GREEN_PIN, GPIO.HIGH)
        GPIO.output(self.BLUE_PIN, GPIO.HIGH)
        
    def red(self):
        GPIO.output(self.RED_PIN, GPIO.HIGH)
        GPIO.output(self.GREEN_PIN, GPIO.LOW)
        GPIO.output(self.BLUE_PIN, GPIO.LOW)
    
    def green(self):
        GPIO.output(self.RED_PIN, GPIO.LOW)
        GPIO.output(self.GREEN_PIN, GPIO.HIGH)
        GPIO.output(self.BLUE_PIN, GPIO.LOW)
        
    def blue(self):
        GPIO.output(self.RED_PIN, GPIO.LOW)
        GPIO.output(self.GREEN_PIN, GPIO.LOW)
        GPIO.output(self.BLUE_PIN, GPIO.HIGH)
    
    def yellow(self):
        GPIO.output(self.RED_PIN, GPIO.HIGH)
        GPIO.output(self.GREEN_PIN, GPIO.HIGH)
        GPIO.output(self.BLUE_PIN, GPIO.LOW)
        
    def purple(self):
        GPIO.output(self.RED_PIN, GPIO.HIGH)
        GPIO.output(self.GREEN_PIN, GPIO.LOW)
        GPIO.output(self.BLUE_PIN, GPIO.HIGH)
        
    def lightBlue(self):
        GPIO.output(self.RED_PIN, GPIO.LOW)
        GPIO.output(self.GREEN_PIN, GPIO.HIGH)
        GPIO.output(self.BLUE_PIN, GPIO.HIGH)
        
    def handle_ir_message(self, data):
        self.button = data["value"]
        
    
    def run(self):
        mqtt_client = mqtt.Client()
        mqtt_client.connect(SERVER_IP, 1883, 60)
        mqtt_client.loop_start()
        mqtt_client.subscribe("IR") # prima info sa servera
        mqtt_client.on_message = lambda client, userdata, message: self.handle_ir_message(json.loads(message.payload.decode('utf-8')))
        self.turnOff()
        
        while True:
            if self.button != "":
                if self.button == "1":
                    self.red()
                    time.sleep(2)
                    self.callback("RED", self.settings)
                elif self.button == "2":
                    self.green()
                    time.sleep(2)
                    self.callback("GREEN", self.settings)
                elif self.button == "3":
                    self.blue()
                    time.sleep(2)
                    self.callback("BLUE", self.settings)
                elif self.button == "4":
                    self.yellow()
                    time.sleep(2)
                    self.callback("YELLOW", self.settings)
                elif self.button == "5":
                    self.purple()
                    time.sleep(2)
                    self.callback("PURPLE", self.settings)
                elif self.button == "6":
                    self.lightBlue()
                    time.sleep(2)
                    self.callback("LIGHT_BLUE", self.settings)
                elif self.button == "7":
                    self.turnOff()
