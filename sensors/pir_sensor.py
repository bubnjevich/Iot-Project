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
		# TODO: kada pir1 detektuje pokret potrebno je ukljuciti DL1 na 10 sekundi (aktuator)
		# TODO: Kada DPIR1 detektuje pokret, na osnovu distance detektovane pomoću DUS1 u prethodnih nekoliko sekundi
		#  ustanoviti da li osoba ulazi ili izlazi u objekat.
		#  Isto logiku primeniti na DPIR2 i DUS2
		#  Čuvati brojno stanje osoba u objektu.
		if self.running_flag:
			self.output_queue.put("DETECTED")

	def no_motion(self, channel):
		if self.running_flag:
			self.output_queue.put("NOT DETECTED")
