from simulators.dus_simulator import DoorUltrasonicSensorSimulator
from broker_settings import HOSTNAME, PORT
import paho.mqtt.publish as publish
import json
from datetime import datetime
import threading


dus_batch = []
publish_data_counter = 0
publish_data_limit = 5
counter_lock = threading.Lock()


def publisher_task(event, dus_batch):
    global publish_data_counter, publish_data_limit
    while True:
        event.wait()
        with counter_lock:
            local_dht_batch = dus_batch.copy()
            publish_data_counter = 0
            dus_batch.clear()
        #print(local_dht_batch)
        publish.multiple(local_dht_batch, hostname=HOSTNAME, port=PORT)
        print(f'published {publish_data_limit} dus values')
        event.clear()


publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, dus_batch,))
publisher_thread.daemon = True
publisher_thread.start()

def dus_callback(distance, dus_settings, publish_event):
    global publish_data_counter, publish_data_limit

    current_timestamp = datetime.utcnow().isoformat()

    status_payload = {
        "measurement": "Distance",
        "simulated": dus_settings['simulated'],
        "runs_on": dus_settings["runs_on"],
        "name": dus_settings["name"],
        "value": distance,
        "time": current_timestamp
    }

    with counter_lock:
        dus_batch.append(('Distance', json.dumps(status_payload), 0, True))
        publish_data_counter += 1

    if publish_data_counter >= publish_data_limit:
        publish_event.set()

def run_dus(settings, threads_list, output_queue):
        if settings['simulated']:
            dus1_simulator = DoorUltrasonicSensorSimulator(output_queue, dus_callback, settings, publish_event)
            dus1_simulator.start()
            threads_list.append(dus1_simulator)
        else:
            from sensors.dus_sensor import UltrasonicDistanceSensor
            dus = UltrasonicDistanceSensor(settings["TRIG_PIN"], settings["ECHO_PIN"], settings, output_queue, dus_callback, publish_event)
            dus.start()
            threads_list.append(dus)
