import threading
import time

try:
	import RPi.GPIO as GPIO
except:
	pass

class UltrasonicDistanceSensor(threading.Thread):
	def __init__(self, TRIG_PIN, ECHO_PIN, settings, output_queue, callback, publish_event):
		super().__init__()
		self.TRIG_PIN = TRIG_PIN
		self.ECHO_PIN = ECHO_PIN
		self.output_queue = output_queue
		self.running_flag = True
		self.callback = callback
		self.publish_event = publish_event
		self.settings = settings

	def setup(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.TRIG_PIN, GPIO.OUT)
		GPIO.setup(self.ECHO_PIN, GPIO.IN)

	def get_distance(self):
		GPIO.output(self.TRIG_PIN, False)
		time.sleep(0.2)
		GPIO.output(self.TRIG_PIN, True)
		time.sleep(0.00001)
		GPIO.output(self.TRIG_PIN, False)
		pulse_start_time = time.time()
		pulse_end_time = time.time()

		max_iter = 100

		iter = 0
		while GPIO.input(self.ECHO_PIN) == 0:
			if iter > max_iter:
				return None
			pulse_start_time = time.time()
			iter += 1

		iter = 0
		while GPIO.input(self.ECHO_PIN) == 1:
			if iter > max_iter:
				return None
			pulse_end_time = time.time()
			iter += 1

		pulse_duration = pulse_end_time - pulse_start_time
		distance = (pulse_duration * 34300)/2
		return distance

	def run(self):
		while True:
			distance = self.get_distance()
			if self.running_flag:
				if distance is not None:
					#self.output_queue.put(f'Distance: {distance} cm')
					self.callback(distance, self.settings, self.publish_event)
					time.sleep(1)
				else:
					self.output_queue.put('Measurement timed out')
				time.sleep(1)
