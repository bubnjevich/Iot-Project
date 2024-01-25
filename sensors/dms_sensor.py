import threading
import time
from datetime import datetime
import json
from broker_settings import SERVER_IP
import paho.mqtt.client as mqtt

try:
	import RPi.GPIO as GPIO
except:
	pass

class MembraneKeypad(threading.Thread):
	def __init__(self, settings, output_queue, callback, publish_event):
		super().__init__()
		self.output_queue = output_queue
		self.running_flag = True
		self.callback = callback
		self.settings = settings
		self.publish_event = publish_event
		self.R1 = settings["R1"]
		self.R2 = settings["R2"]
		self.R3 = settings["R3"]
		self.R4 = settings["R4"]
		self.C1 = settings["C1"]
		self.C2 = settings["C2"]
		self.C3 = settings["C3"]
		self.C4 = settings["C4"]
		self.l = ""
		self.mqtt_client = mqtt.Client()

		self.setup()

	def setup(self):
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM)

		GPIO.setup(self.R1, GPIO.OUT)
		GPIO.setup(self.R2, GPIO.OUT)
		GPIO.setup(self.R3, GPIO.OUT)
		GPIO.setup(self.R4, GPIO.OUT)

		GPIO.setup(self.C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		GPIO.setup(self.C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		GPIO.setup(self.C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		GPIO.setup(self.C4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

	def send_dms(self,  digits):
		# print("SALJEM DMS: ", digits)
		current_timestamp = datetime.utcnow().isoformat()
		status_payload = {
			"measurement": "DMS",
			"device_name": self.settings["name"],
			"simulated": False,
			"runs_on": self.settings["runs_on"],
			"name": self.settings["name"],
			"value": digits,
			"time": current_timestamp
		}

		self.mqtt_client.publish("DMS", json.dumps(status_payload))

	def readLine(self, line, characters):
		GPIO.output(line, GPIO.HIGH)
		if(GPIO.input(self.C1) == 1):
			self.l += characters[0]
			#self.callback(characters[0], self.settings, self.publish_event)
		if(GPIO.input(self.C2) == 1):
			self.l += characters[1]
			#self.callback(characters[1], self.settings, self.publish_event)
		if(GPIO.input(self.C3) == 1):
			self.l += characters[2]

			#self.callback(characters[2], self.settings, self.publish_event)
		if(GPIO.input(self.C4) == 1):
			self.l += characters[3]
			#self.callback(characters[3], self.settings, self.publish_event)
		if len(self.l) == 4:
			self.send_dms(self.l)
			self.l = ""
		GPIO.output(line, GPIO.LOW)

	def run(self):
		self.mqtt_client.connect(SERVER_IP, 1883, 60)
		self.mqtt_client.loop_start()
		while True:
			if self.running_flag:
				self.readLine(self.R1, ["1","2","3","A"])
				self.readLine(self.R2, ["4","5","6","B"])
				self.readLine(self.R3, ["7","8","9","C"])
				self.readLine(self.R4, ["*","0","#","D"])
				time.sleep(0.2)
