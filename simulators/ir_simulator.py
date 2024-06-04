import threading
import random
import time


class BIRSimulator(threading.Thread):
	def __init__(self, callback, output, settings):
		super().__init__()
		self.output = output
		self.callback = callback
		self.settings = settings
		self.ButtonsNames = ["LEFT", "RIGHT", "UP", "DOWN", "2", "3", "1", "OK", "4", "5", "6", "7", "8", "9", "*", "0",
							 "#"]
	def run(self):
		while True:
			motion = random.choice(self.ButtonsNames)
			self.output.put(motion)
			# self.callback(motion, self.settings) TODO: otkomentarisati
			time.sleep(20)