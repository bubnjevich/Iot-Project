from queue import Queue
import time
from configuration.configuration import load_settings
from components.dht_controller import run_dht
from components.dms_controller import run_dms
from components.dl_controller import run_dl
from components.ds_controller import run_ds
from components.dus_controller import run_dus
from components.pir_controller import run_pir
from components.db_controller import run_db
from components.gsg_controller import run_gsg
from components.lcd_controller import run_lcd
from components.four_sd_controller import run_4sd
import sys


try:
	import RPi.GPIO as GPIO
	GPIO.setmode(GPIO.BCM)
except:
	pass

	
def get_option():
	while True:
		print("1. Get device output")
		print("2. Stop device")
		try:
			choice = int(input("Enter the number of the IoT device option: "))
			if  0 > choice > 2:
				print("Bad input")
				continue
			else:
				return choice
		except:
			print("Bad input")
			continue

def get_device(menu, length):
	while True:
		print(menu)
		try:
			choice = int(input("Enter the number of the IoT device (Ctrl+C to exit): "))
			if  0 > choice > length:
				print("Bad input")
				continue
			else:
				return choice
		except:
			print("Bad input")
			continue
		

def start_threads(thread_list, output_queue, settings, pi_number):
	pi_items = settings.items()["PI" + pi_number]
	for key, device_settings in pi_items:
		print(device_settings["name"])
		device_type = device_settings['device_type']
		function_name = "run_" + device_type
		controller_function = globals().get(function_name)
		if controller_function and callable(controller_function):
			controller_function(device_settings, thread_list, output_queue)
		else:
			print(f"No controller function found for device type: {device_type}")

def main(pi_number):
	output_queue = Queue()
	settings = load_settings()
	thread_list = []
	start_threads(thread_list, output_queue, settings, pi_number)
		


if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Usage: python3 main.py [PI_NUMBER]")
		sys.exit(1)

	pi_number = sys.argv[1]
	print(f"Running on Raspberry Pi number: {pi_number}")
	main(pi_number)
