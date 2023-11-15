import threading
import time
from typing import Any

try:
	import RPi.GPIO as GPIO
except:
	pass


class Buzzer(threading.Thread):
	def __init__(self, pin, ):
		self.running_flag = False
		self.pin = pin
	
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
		self.setup()
		while True:
			if self.running_flag:
				pitch = 440
				duration = 0.1
				self.buzz(pitch, duration)
				self.running_flag = False
				time.sleep(1)

