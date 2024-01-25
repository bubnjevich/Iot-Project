from simulators.rgb_simulator import RGBimulator
import threading
from broker_settings import HOSTNAME, PORT
import paho.mqtt.publish as publish
import json
from datetime import datetime
import paho.mqtt.client as mqtt


rgb_batch = []
publish_data_counter = 0
publish_data_limit = 5
counter_lock = threading.Lock()


def publisher_task(event, rgb_batch):
    global publish_data_counter, publish_data_limit
    while True:
        event.wait()
        with counter_lock:
            local_rgb_batch = rgb_batch.copy()
            publish_data_counter = 0
            rgb_batch.clear()
        publish.multiple(local_rgb_batch, hostname=HOSTNAME, port=PORT)
        print(f'published {publish_data_limit} pir values')
        event.clear()


publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, rgb_batch,))
publisher_thread.daemon = True
publisher_thread.start()

def rgb_callback(status, rgb_settings, publish_event):
    global publish_data_counter, publish_data_limit

    current_timestamp = datetime.utcnow().isoformat()

    status_payload = {
        "measurement": "Motion",
        "simulated": rgb_settings['simulated'],
        "runs_on": rgb_settings["runs_on"],
        "name": rgb_settings["name"],
        "value": status , # 0 ili 1,
        "time": current_timestamp
    }

    with counter_lock:
        rgb_batch.append(('Motion', json.dumps(status_payload), 0, True))
        publish_data_counter += 1

    if publish_data_counter >= publish_data_limit:
        publish_event.set()



def run_rgb(settings, threads_list, output_queue):

        if settings['simulated']:
            rgb_simulator = RGBimulator(output_queue, rgb_callback, settings, publish_event)
            rgb_simulator.start()
            threads_list.append(rgb_simulator)
        else:
            from actuators.rgb import RGBLED
            rgb = RGBLED(output_queue, rgb_callback, settings, publish_event)
            rgb.start()
            threads_list.append(rgb)
