from datetime import datetime
from simulators.dht_simulator import DHTSimulator
import json
import paho.mqtt.publish as publish
from broker_settings import HOSTNAME, PORT


import threading


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
        # print(f'published {publish_data_limit} dht values')
        event.clear()


publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, dht_batch,))
publisher_thread.daemon = True
publisher_thread.start()


def dht_callback(humidity, temperature,dht_settings, publish_event):
    global publish_data_counter, publish_data_limit

    # Current timestamp
    current_timestamp = datetime.utcnow().isoformat()
    temp_payload = {
        "measurement": "Temperature",
        "simulated": dht_settings['simulated'],
        "runs_on": dht_settings["runs_on"],
        "name": dht_settings["name"],
        "value": temperature,
        "time": current_timestamp
    }

    humidity_payload = {
        "measurement": "Humidity",
        "simulated": dht_settings['simulated'],
        "runs_on": dht_settings["runs_on"],
        "name": dht_settings["name"],
        "value": humidity,
        "time": current_timestamp
    }

    with counter_lock:
        dht_batch.append(('Temperature', json.dumps(temp_payload), 0, True))
        dht_batch.append(('Humidity', json.dumps(humidity_payload), 0, True))
        publish_data_counter += 1

    if publish_data_counter >= publish_data_limit:
        publish_event.set()

def run_dht(settings, threads_list, output_queue):
        if settings['simulated']:
            dht_simulator = DHTSimulator(output_queue, dht_callback, settings, publish_event)
            dht_simulator.start()
            threads_list.append(dht_simulator)
        else:
            from sensors.dht_sensor import DHT
            dht_sensor = DHT(settings['pin'], output_queue, dht_callback, settings, publish_event)
            dht_sensor.start()
            threads_list.append(dht_sensor)
