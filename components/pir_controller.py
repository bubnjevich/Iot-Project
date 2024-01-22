from simulators.pir_simulator import MotionSensorSimulator
import threading
from simulators.ds_simulator import DoorSensorSimulator
from broker_settings import HOSTNAME, PORT
import paho.mqtt.publish as publish
import json
from datetime import datetime


pir_batch = []
publish_data_counter = 0
publish_data_limit = 5
counter_lock = threading.Lock()


def publisher_task(event, pir_batch):
    global publish_data_counter, publish_data_limit
    while True:
        event.wait()
        with counter_lock:
            local_dht_batch = pir_batch.copy()
            publish_data_counter = 0
            pir_batch.clear()
        publish.multiple(local_dht_batch, hostname=HOSTNAME, port=PORT)
        # print(f'published {publish_data_limit} pir values')
        event.clear()


publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, pir_batch,))
publisher_thread.daemon = True
publisher_thread.start()

threads_list_copy = []
door_light_thread = None
dus1_thread = None
dus2_thread = None

def pir_callback(status, pir_settings, publish_event, pir_thread):
    global publish_data_counter, publish_data_limit
    global door_light_thread, dus1_thread, dus2_thread

    if door_light_thread is None or dus1_thread is None or dus2_thread is None:
        for thread in threads_list_copy:
            if thread.name == 'DoorLightThread':
                door_light_thread = thread
            elif thread.name == "DUS1":
                dus1_thread = thread
            elif thread.name == "DUS2":
                dus2_thread = thread

    """ if motion is detected on DPIR1 turn on DL for 10 seconds and check DUS1 """
    if pir_settings["name"] == "DPIR1" and status == 1:
        door_light_thread.state = True
        if dus1_thread.last_distances[1] - dus1_thread.last_distances[0] > 0: # osoba izlazi iz objekta
            pir_thread.current_number = max(0, pir_thread.current_number - 1)
        else:
            pir_thread.current_number += 1

    elif pir_settings["name"] == "DPIR2" and status == 1:
        if dus2_thread.last_distances[1] - dus2_thread.last_distances[0] > 0:  # osoba izlazi iz objekta
            pir_thread.current_number = max(0, pir_thread.current_number - 1)
        else:
            pir_thread.current_number += 1






    current_timestamp = datetime.utcnow().isoformat()

    status_payload = {
        "measurement": "Motion",
        "simulated": pir_settings['simulated'],
        "runs_on": pir_settings["runs_on"],
        "name": pir_settings["name"],
        "value": status , # 0 ili 1,
        "time": current_timestamp
    }

    with counter_lock:
        pir_batch.append(('Motion', json.dumps(status_payload), 0, True))
        publish_data_counter += 1

    if publish_data_counter >= publish_data_limit:
        publish_event.set()

def run_pir(settings, threads_list, output_queue):
    global threads_list_copy
    threads_list_copy = threads_list
    if settings['simulated']:
        pir_simulator = MotionSensorSimulator(output_queue, pir_callback, settings, publish_event)
        pir_simulator.start()
        threads_list.append(pir_simulator)
    else:
        from sensors.pir_sensor import PIRMotionSensor
        pir = PIRMotionSensor(settings['pin'], output_queue, pir_callback, settings, publish_event)
        pir.start()
        threads_list.append(pir)
