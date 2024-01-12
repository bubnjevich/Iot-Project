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

try:
	import RPi.GPIO as GPIO
	GPIO.setmode(GPIO.BCM)
except:
	pass


def get_menu(settings):
	menu = "IoT Device Menu:\n"
	i = 1
	for key, device_settings in settings.items():
		device_name = device_settings['name']
		menu += str(i) + ". " + device_name + "\n"
		i += 1
	return menu
	
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
		

def start_threads(thread_list, output_queue, settings):
	for key, device_settings in settings.items():
		device_type = device_settings['device_type']
		function_name = "run_" + device_type
		if (device_type != "dht"):
			continue

		controller_function = globals().get(function_name)

		if controller_function and callable(controller_function):
			controller_function(device_settings, thread_list, output_queue)
		else:
			print(f"No controller function found for device type: {device_type}")

def main():
	output_queue = Queue()
	settings = load_settings()
	thread_list = []
	menu= get_menu(settings)
	start_threads(thread_list, output_queue, settings)
	menu_flag = True
	
	while True:
		try:
			if menu_flag:
				device_num = get_device(menu, len(settings.items()))
				selected_thread = thread_list[device_num - 1]
			else:
				output = output_queue.get()
				print(output)
			time.sleep(1)
		except KeyboardInterrupt:
			menu_flag = True
			while not output_queue.empty():
				output = output_queue.get()
			for thread in thread_list:
				thread.running_flag = False
		


if __name__ == "__main__":
	main()
