import threading
import time
try:
	import RPi.GPIO as GPIO
except:
	pass

class D4S7(threading.Thread):

	def __init__(self):
		super().__init__()
		# GPIO ports for the 7seg pins
		self.segments = (11, 4, 23, 8, 7, 10, 18, 25)
		self.digits = (22, 27, 17, 24)
		self.num = {' ':(0,0,0,0,0,0,0),
                    '0':(1,1,1,1,1,1,0),
                    '1':(0,1,1,0,0,0,0),
                    '2':(1,1,0,1,1,0,1),
                    '3':(1,1,1,1,0,0,1),
                    '4':(0,1,1,0,0,1,1),
                    '5':(1,0,1,1,0,1,1),
                    '6':(1,0,1,1,1,1,1),
                    '7':(1,1,1,0,0,0,0),
                    '8':(1,1,1,1,1,1,1),
                    '9':(1,1,1,1,0,1,1)}



	def setup(self):
		GPIO.setmode(GPIO.BCM)
		for segment in self.segments:
			GPIO.setup(segment, GPIO.OUT)
			GPIO.output(segment, 0)

		for digit in self.digits:
			GPIO.setup(digit, GPIO.OUT)
			GPIO.output(digit, 1)


	def run(self) -> None:
		self.setup()
		try:
			while True:
				current_time = time.strftime("%H%M")  # Formatira trenutno vreme u "satminut" format
				for digit in range(4):
					for loop in range(0, 7):
						GPIO.output(self.segments[loop], self.num[current_time[digit]][loop])
						if (int(time.strftime("%S")[0]) % 2 == 0) and (digit == 1):
							GPIO.output(25, 1)
						else:
							GPIO.output(25, 0)
					GPIO.output(self.digits[digit], 0)
					time.sleep(0.001)
					GPIO.output(self.digits[digit], 1)
		finally:
			GPIO.cleanup()