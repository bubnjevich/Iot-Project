import threading
import json
from datetime import datetime
import paho.mqtt.publish as publish
from broker_settings import  PORT, SERVER_IP
from simulators.dms_simulator import DoorMembraneSwitchSimulator

dms_batch = []
publish_data_counter = 0
publish_data_limit = 5
counter_lock = threading.Lock()

def publisher_task(event, dht_batch):
    global publish_data_counter, publish_data_limit, dms_value_to_send
    while True:
        event.wait()
        with counter_lock:
            local_dht_batch = dht_batch.copy()
            publish_data_counter = 0
            dht_batch.clear()
        publish.multiple(local_dht_batch, hostname=SERVER_IP, port=PORT)
        dms_value_to_send = ""
        #print(f'published {publish_data_limit} dms values')
        event.clear()


publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, dms_batch,))
publisher_thread.daemon = True
publisher_thread.start()
dms_value_to_send = ""

def dms_callback(dms_value, dms_settings, publish_event):
    global publish_data_counter, publish_data_limit, dms_value_to_send

    if not dms_settings['simulated']:
        if len(dms_value_to_send) != 3:
            dms_value_to_send += str(dms_value)
        else:
            dms_value_to_send += str(dms_value)
            current_timestamp = datetime.utcnow().isoformat()
            payload = {
                "measurement": "MembraneSwitch",
                "simulated": False,
                "runs_on": dms_settings["runs_on"],
                "name": dms_settings["name"],
                "value": dms_value_to_send,
                "time": current_timestamp
            }

            with counter_lock:
                dms_batch.append(('MembraneSwitch', json.dumps(payload), 0, True))
                publish_event.set() # odmah salji


    # Current timestamp
    current_timestamp = datetime.utcnow().isoformat()
    payload = {
        "measurement": "MembraneSwitch",
        "simulated": dms_settings['simulated'],
        "runs_on": dms_settings["runs_on"],
        "name": dms_settings["name"],
        "value": str(dms_value),
        "time": current_timestamp
    }

    with counter_lock:
        dms_batch.append(('MembraneSwitch', json.dumps(payload), 0, True))
        publish_data_counter += 1

    if publish_data_counter >= publish_data_limit:
        publish_event.set()

def run_dms(settings, threads_list, output_queue):
        if settings['simulated']:
            dms_simulator = DoorMembraneSwitchSimulator(output_queue, dms_callback, settings, publish_event)
            dms_simulator.start()
            threads_list.append(dms_simulator)
        else:
            from sensors.dms_sensor import MembraneKeypad
            dms = MembraneKeypad(settings, output_queue)
            dms.start()
            threads_list.append(dms)
