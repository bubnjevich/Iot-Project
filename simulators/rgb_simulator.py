import threading
import json
from broker_settings import SERVER_IP
import paho.mqtt.client as mqtt
import time

class RGBSimulator(threading.Thread):
	
	def __init__(self, callback, output_queue, settings):
		super().__init__()
		self.output_queue = output_queue
		self.callback = callback
		self.settings = settings
		self.button = ""
	
	def handle_ir_message(self, data):
		self.button = data["value"]
	
	def run(self):
		mqtt_client = mqtt.Client()
		mqtt_client.connect(SERVER_IP, 1883, 60)
		mqtt_client.loop_start()
		mqtt_client.subscribe("IR")  # prima info sa servera
		mqtt_client.on_message = lambda client, userdata, message: self.handle_ir_message(
			json.loads(message.payload.decode('utf-8')))
		while True:
			if self.button != "":
				if self.button == "1":
					print("RED")
					self.output_queue.put("RED")
					time.sleep(2)
					self.callback("RED", self.settings)
				elif self.button == "2":
					print("GREEN")
					self.output_queue.put("GREEN")
					time.sleep(2)
					self.callback("GREEN", self.settings)
				elif self.button == "3":
					self.output_queue.put("BLUE")
					time.sleep(2)
					self.callback("BLUE", self.settings)
				elif self.button == "4":
					self.output_queue.put("YELLOW")
					time.sleep(2)
					self.callback("YELLOW", self.settings)
				elif self.button == "5":
					self.output_queue.put("PURPLE")
					time.sleep(2)
					self.callback("PURPLE", self.settings)
				elif self.button == "6":
					self.output_queue.put("LIGHT_BLUE")
					time.sleep(2)
					self.callback("LIGHT_BLUE", self.settings)
				elif self.button == "7":
					self.output_queue.put("OFF")
					self.callback("OFF", self.settings)
					self.button = ""

		