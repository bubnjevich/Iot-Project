import threading
import time
from typing import Any
import paho.mqtt.client as mqtt
import json
from broker_settings import SERVER_IP

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
		self.running_clock = False
		self.system_active = False  # inicijalno sistem alarma je ugasen, pali se preko DMS-a
		self.pin = ""

		self.alarm_list = []

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

	def play(self):
		""" Melodija za budilnik """
		t = 0
		notes = [262, 294, 330, 262, 262, 294, 330, 262, 330, 349, 392, 330, 349, 392, 392, 440, 392, 349, 330, 262,
				 392, 440, 392, 349, 330, 262, 262, 196, 262, 262, 196, 262]
		duration = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1, 0.5, 0.5, 1, 0.25, 0.25, 0.25, 0.25, 0.5, 0.5,
					0.25, 0.25, 0.25, 0.25, 0.5, 0.5, 0.5, 0.5, 1, 0.5, 0.5, 1]
		for n in notes:
			self.buzz(n, duration[t])
			time.sleep(duration[t] * 0.1)
			t += 1

	def handle_alarm(self, data, mqtt_client):
		if data["measurement"] == "Clock":
			self.running_clock = data["value"]
			return

		if data["measurement"] == "DMS":
			if self.pin == "" and not data["simulated"]:  # ako korisnik prvi put unosi DMS
				# print("postavio self.pin na ", data["value"])
				self.pin = data["value"]
				time.sleep(10)
				self.system_active = True
			else:
				if data["value"] == self.pin:
					if self.running_flag:  # ako je upaljen alarm
						# print("Alarm/i je bio upaljen SVE gasim...")
						self.running_flag = False
						self.system_active = False
						self.alarm_list = []

					elif not self.system_active:  # nije sistem aktivan
						# print("Sistem nije bio aktivan. Aktiviracu sistem alarma za 10 sekundi.....")
						time.sleep(10)  # aktiviraj nakon 10 sekundi
						self.system_active = True
			return

		if self.system_active:
			if data["start"]:  # ako je aktivan sistem i treba da se upali alarm
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
		mqtt_client.subscribe("AlarmAlerted")
		if self.settings["name"] == "Bedroom Buzzer":
			mqtt_client.subscribe("Clock")
		mqtt_client.on_message = lambda client, userdata, message: self.handle_alarm(json.loads(message.payload.decode('utf-8')), mqtt_client)
		self.setup()
		while True:
			if self.running_clock:
				self.play()
			elif self.running_flag:
				pitch = 440
				duration = 0.1
				self.buzz(pitch, duration)
				self.callback(1, self.settings, self.publish_event)
				self.running_flag = False
				time.sleep(1)

