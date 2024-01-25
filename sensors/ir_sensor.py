import threading
from broker_settings import PI3
from datetime import datetime
import time
import paho.mqtt.client as mqtt

try:
	import RPi.GPIO as GPIO
except:
	pass



class IRResiver(threading.Thread):

    def __init__(self, pin, output_queue, callback, settings, publish_event):
        super().__init__()
        self.pin = pin
        self.output_queue = output_queue
        self.running_flag = True
        self.settings = settings
        self.callback = callback
        self.publish_event = publish_event
        self.button = [0x300ff22dd, 0x300ffc23d, 0x300ff629d, 0x300ffa857, 0x300ff9867, 0x300ffb04f, 0x300ff6897, 0x300ff02fd, 0x300ff30cf, 0x300ff18e7, 0x300ff7a85, 0x300ff10ef, 0x300ff38c7, 0x300ff5aa5, 0x300ff42bd, 0x300ff4ab5, 0x300ff52ad]  # HEX code list
        self.buttons_names = ["LEFT",   "RIGHT",      "UP",       "DOWN",       "2",          "3",          "1",        "OK",        "4",         "5",         "6",         "7",         "8",          "9",        "*",         "0",        "#"]  # String list in same order as HEX list


    def setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)

    def getBinary(self):
        num1s = 0 
        binary = 1  
        command = [] 
        previousValue = 0  
        value = GPIO.input(self.pin)  

        while value:
            time.sleep(0.0001)
            value = GPIO.input(self.pin)
            
        startTime = datetime.now()
        
        while True:
            if previousValue != value:
                now = datetime.now()
                pulseTime = now - startTime
                startTime = now 
                command.append((previousValue, pulseTime.microseconds)) 
                
            if value:
                num1s += 1
            else:
                num1s = 0
            
            if num1s > 10000:
                break
                
            previousValue = value
            value = GPIO.input(self.pin)
            
        for (typ, tme) in command:
            if typ == 1: 
                if tme > 1000: 
                    binary = binary *10 +1 
                else:
                    binary *= 10 
                
        if len(str(binary)) > 34: 
            binary = int(str(binary)[:34])
            
        return binary
        
    def convertHex(self, binaryValue):
        tmpB2 = int(str(binaryValue),2) 
        return hex(tmpB2)
        
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
                inData = self.convertHex(self.getBinary()) 
                for button in range(len(self.buttons)):
                    if hex(self.buttons[button]) == inData: 
                        self.callback(button, self.settings, self.publish_event)
                        try:
                            color = button_to_color.get(button, "")     
                            mqtt_client.publish("LightChange", color)
                        except:
                            pass
