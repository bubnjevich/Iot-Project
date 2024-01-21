import threading
import time
try:
	import RPi.GPIO as GPIO
except:
	pass

class Button(threading.Thread):
	def __init__(self, port, output_queue, callback, settings, publish_event):
		super().__init__()
		self.port = port
		self.output_queue = output_queue
		self.running_flag = False
		self.callback = callback
		self.publish_event = publish_event
		self.settings = settings


	def run(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.port, GPIO.IN, pull_up_down = GPIO.PUD_UP)
		GPIO.add_event_detect(self.port, GPIO.RISING, callback = self.button_pressed, bouncetime = 100)
		GPIO.add_event_detect(self.pin, GPIO.FALLING, callback=self.button_released)

	def button_pressed(self, event):
		if self.running_flag:
			self.callback("Unlocked", self.settings, self.publish_event)
			#self.output_queue.put("Unlocked") 

	def button_pressed(self, event):
		if self.running_flag:
			self.callback("Locked", self.settings, self.publish_event)
			#self.output_queue.put("Unlocked") 
