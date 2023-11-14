import threading
import time
try:
	import RPi.GPIO as GPIO
except:
	pass

class MembraneKeypad(threading.Thread):
	def __init__(self, settings, output_queue):
		self.output_queue = output_queue
		self.running_flag = False
		self.R1 = settings["R1"]
		self.R2 = settings["R2"]
		self.R3 = settings["R3"]
		self.R4 = settings["R4"]
		self.C1 = settings["C1"]
		self.C2 = settings["C2"]
		self.C3 = settings["C3"]
		self.C4 = settings["C4"]

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

	def readLine(self, line, characters):
		GPIO.output(line, GPIO.HIGH)
		if(GPIO.input(self.C1) == 1):
			self.output_queue.put(characters[0])
		if(GPIO.input(self.C2) == 1):
			self.output_queue.put(characters[1])
		if(GPIO.input(self.C3) == 1):
			self.output_queue.put(characters[2])
		if(GPIO.input(self.C4) == 1):
			self.output_queue.put(characters[3])
		GPIO.output(line, GPIO.LOW)

	def run(self):
		while True:
			if self.running_flag:
				self.readLine(self.R1, ["1","2","3","A"])
				self.readLine(self.R2, ["4","5","6","B"])
				self.readLine(self.R3, ["7","8","9","C"])
				self.readLine(self.R4, ["*","0","#","D"])
				time.sleep(0.2)
