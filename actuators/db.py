import threading
import time
from typing import Any
import paho.mqtt.client as mqtt
import json
from broker_settings import HOSTNAME
import json

try:
	import RPi.GPIO as GPIO
except:
	pass


class Buzzer(threading.Thread):
	def __init__(self, pin, callback, settings, publish_event):
		super().__init__()
		self.running_flag = False
		self.pin = pin
		self.settings = settings
		self.callback = callback
		self.publish_event = publish_event
		self.alarm_list = []

	def handle_alarm(self, data):
		if data["start"]:
			self.running_flag = True
			self.alarm_list.append(data["type"])
		else:
			if len(self.alarm_list) != 0:
				self.alarm_list.remove(data["type"])
			if len(self.alarm_list) == 0:
				self.running_flag = False   
	
	def setup(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.pin, GPIO.OUT)
	
	def buzz(self, pitch, duration):
		period = 1.0 / pitch
		delay = period / 2
		cycles = int(duration * pitch)
		for i in range(cycles):
			GPIO.output(self.pin, True)
			time.sleep(delay)
			GPIO.output(self.pin, False)
			time.sleep(delay)
	
	def run(self):
		mqtt_client = mqtt.Client()
		mqtt_client.connect(HOSTNAME, 1883, 60)
		mqtt_client.loop_start()
		mqtt_client.subscribe("AlarmAlerted")
		mqtt_client.on_message = lambda client, userdata, message: self.handle_alarm(json.loads(message.payload.decode('utf-8')))

		self.setup()
		while True:
			if self.running_flag:
				pitch = 440
				duration = 0.1
				self.buzz(pitch, duration)
				self.callback(1, self.settings, self.publish_event)
				self.running_flag = False
				time.sleep(1)

