import json
from datetime import datetime
import threading
from broker_settings import PORT, SERVER_IP
import paho.mqtt.publish as publish

dht_batch = []
publish_data_counter = 0
publish_data_limit = 5
counter_lock = threading.Lock()


def publisher_task(event, dht_batch):
	global publish_data_counter, publish_data_limit
	while True:
		event.wait()
		with counter_lock:
			local_dht_batch = dht_batch.copy()
			publish_data_counter = 0
			dht_batch.clear()
		publish.multiple(local_dht_batch, hostname=SERVER_IP, port=PORT)
		event.clear()


publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, dht_batch,))
publisher_thread.daemon = True
publisher_thread.start()

def bir_callback(button, settings):
	global publish_data_counter, publish_data_limit

	current_timestamp = datetime.utcnow().isoformat()
	temp_payload = {
		"measurement": "BIR",
		"simulated": settings['simulated'],
		"runs_on": settings["runs_on"],
		"name": settings["name"],
		"value": button,
		"time": current_timestamp
	}
	with counter_lock:
		dht_batch.append(('BIR', json.dumps(temp_payload), 0, True))
		publish_data_counter += 1
	
	if publish_data_counter >= publish_data_limit:
		publish_event.set()


def run_ir(settings, threads_list, output_queue):
	if settings["simulated"]:
		from simulators.ir_simulator import BIRSimulator
		bir = BIRSimulator(bir_callback, output_queue, settings)
		bir.start()
		threads_list.append(bir)
	else:
		from sensors.ir_sensor import Bir
		bir = Bir(bir_callback, output_queue, settings)
		bir.start()
		threads_list.append(bir)