from simulators.ir_simulator import IRSimulator
from broker_settings import HOSTNAME, PORT
import paho.mqtt.publish as publish
import json
from datetime import datetime
import threading


ir_batch = []
publish_data_counter = 0
publish_data_limit = 1
counter_lock = threading.Lock()


def publisher_task(event, ir_batch):
    global publish_data_counter, publish_data_limit
    while True:
        event.wait()
        with counter_lock:
            local_ir_batch = ir_batch.copy()
            publish_data_counter = 0
            ir_batch.clear()
        publish.multiple(local_ir_batch, hostname=HOSTNAME, port=PORT)
        print(f'published {publish_data_limit} ir values')
        event.clear()


publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, ir_batch,))
publisher_thread.daemon = True
publisher_thread.start()

def ir_callback(remote_value, ir_settings, publish_event):
    global publish_data_counter, publish_data_limit

    current_timestamp = datetime.utcnow().isoformat()

    status_payload = {
        "measurement": "Remote",
        "simulated": ir_settings['simulated'],
        "runs_on": ir_settings["runs_on"],
        "name": ir_settings["name"],
        "value": remote_value,
        "time": current_timestamp
    }

    with counter_lock:
        ir_batch.append(('Remote', json.dumps(status_payload), 0, True))
        publish_data_counter += 1

    if publish_data_counter >= publish_data_limit:
        publish_event.set()

def run_ir(settings, threads_list, output_queue):
        if settings['simulated']:
            ir_simulator = IRSimulator(output_queue, ir_callback, settings, publish_event)
            ir_simulator.start()
            threads_list.append(ir_simulator)
        else:
            from sensors.ir_sensor import IRResiver
            ir = IRResiver(settings["pin"], settings, output_queue, ir_callback, publish_event)
            ir.start()
            threads_list.append(ir)
