import threading

try:
	import RPi.GPIO as GPIO
except:
	pass

class PIRMotionSensor(threading.Thread):
	def __init__(self, pin, output_queue):
		super().__init__()
		self.pin = pin
		self.output_queue = output_queue
		self.running_flag = False

	def setup(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.pin, GPIO.IN)
		GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.motion_detected)
		GPIO.add_event_detect(self.pin, GPIO.FALLING, callback=self.no_motion)

	def run(self):
		self.setup()

	def motion_detected(self, channel):
		if self.running_flag:
			self.output_queue.put("Motion Sensor Status: DETECTED")

	def no_motion(self, channel):
		if self.running_flag:
			self.output_queue.put("Motion Sensor Status: NOT DETECTED")
