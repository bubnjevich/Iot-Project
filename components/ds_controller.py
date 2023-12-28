import threading
import time
from simulators.ds_simulator import DoorSensorSimulator
from broker_settings import HOSTNAME, PORT
import paho.mqtt.publish as publish
import json


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
        publish.multiple(local_dht_batch, hostname=HOSTNAME, port=PORT)
        print(f'published {publish_data_limit} ds values')
        event.clear()


publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, dht_batch,))
publisher_thread.daemon = True
publisher_thread.start()

def ds_callback(status, ds_settings, publish_event):
    global publish_data_counter, publish_data_limit

    status_payload = {
        "measurement": "DoorStatus",
        "simulated": ds_settings['simulated'],
        "runs_on": ds_settings["runs_on"],
        "name": ds_settings["name"],
        "value": status # 0 ili 1
    }

    with counter_lock:
        dht_batch.append(('DoorStatus', json.dumps(status_payload), 0, True))
        publish_data_counter += 1

    if publish_data_counter >= publish_data_limit:
        publish_event.set()

def run_ds(settings, threads_list, output_queue):
        if settings['simulated']:
            ds_simulator = DoorSensorSimulator(output_queue, ds_callback, settings, publish_event)
            ds_simulator.start()
            threads_list.append(ds_simulator)
        else:
            from sensors.ds_sensor import Button
            ds = Button(settings['port'], output_queue)
            ds.start()
            threads_list.append(ds)
