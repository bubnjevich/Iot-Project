from simulators.pir_simulator import MotionSensorSimulator
import threading
from simulators.ds_simulator import DoorSensorSimulator
from broker_settings import HOSTNAME, PORT, SERVER_IP
import paho.mqtt.publish as publish
import json
from datetime import datetime
import paho.mqtt.client as mqtt


pir_batch = []
publish_data_counter = 0
publish_data_limit = 5
counter_lock = threading.Lock()


def publisher_task(event, pir_batch):
    global publish_data_counter, publish_data_limit
    while True:
        event.wait()
        with counter_lock:
            local_pir_batch = pir_batch.copy()
            publish_data_counter = 0
            pir_batch.clear()
        publish.multiple(local_pir_batch, hostname=HOSTNAME, port=PORT)
        print(f'published {publish_data_limit} pir values')
        event.clear()


publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, pir_batch,))
publisher_thread.daemon = True
publisher_thread.start()

def pir_callback(status, pir_settings, publish_event):
    global publish_data_counter, publish_data_limit

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

        if settings['simulated']:
            pir_simulator = MotionSensorSimulator(output_queue, pir_callback, settings, publish_event)
            pir_simulator.start()
            threads_list.append(pir_simulator)
        else:
            from sensors.pir_sensor import PIRMotionSensor
            pir = PIRMotionSensor(settings['pin'], output_queue, pir_callback, settings, publish_event)
            pir.start()
            threads_list.append(pir)
