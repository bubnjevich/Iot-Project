from simulators.dl_simulator import DoorLightSimulator
from datetime import datetime
import json
import paho.mqtt.publish as publish
from broker_settings import HOSTNAME, PORT, SERVER_IP
import threading

dl_batch = []
publish_data_counter = 0
publish_data_limit = 5
counter_lock = threading.Lock()


def publisher_task(event, dl_batch):
    global publish_data_counter, publish_data_limit
    while True:
        event.wait()
        with counter_lock:
            local_dht_batch = dl_batch.copy()
            publish_data_counter = 0
            dl_batch.clear()
        publish.multiple(local_dht_batch, hostname=SERVER_IP, port=PORT)
        #print(f'published {publish_data_limit} dl values')
        event.clear()

publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, dl_batch,))
publisher_thread.daemon = True
publisher_thread.start()

def dl_callback(light, dl_settings, publish_event):
    global publish_data_counter, publish_data_limit

    # Current timestamp
    current_timestamp = datetime.utcnow().isoformat()
    temp_payload = {
        "measurement": "Light",
        "simulated": dl_settings['simulated'],
        "runs_on": dl_settings["runs_on"],
        "name": dl_settings["name"],
        "value": light,
        "time": current_timestamp
    }

    with counter_lock:
        dl_batch.append(('Light', json.dumps(temp_payload), 0, True))
        publish_data_counter += 1

    if publish_data_counter >= publish_data_limit:
        publish_event.set()

def run_dl(settings, threads_list, output_queue):
        if settings['simulated']:
            dl_simulator = DoorLightSimulator(output_queue, dl_callback, settings, publish_event)
            dl_simulator.start()
            threads_list.append(dl_simulator)
        else:
            from actuators.dl import LED
            dl = LED(settings['port'], output_queue, dl_callback, settings, publish_event)
            dl.start()
            threads_list.append(dl)
