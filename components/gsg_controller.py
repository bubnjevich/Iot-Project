from broker_settings import  PORT, SERVER_IP
import paho.mqtt.publish as publish
import json
from datetime import datetime
import threading
from simulators.gsg_simulator import GSGSimulator

gsg_batch = []
publish_data_counter = 0
publish_data_limit = 5
counter_lock = threading.Lock()

def publisher_task(event, gsg_batch):
    global publish_data_counter, publish_data_limit
    while True:
        event.wait()
        with counter_lock:
            local_gsg_batch = gsg_batch.copy()
            publish_data_counter = 0
            gsg_batch.clear()
        #print(local_dht_batch)
        publish.multiple(local_gsg_batch, hostname=SERVER_IP, port=PORT)
        #print(f'published {publish_data_limit} gsg/accel values')
        event.clear()


publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, gsg_batch,))
publisher_thread.daemon = True
publisher_thread.start()

def gsg_callback(accel, gyro, gsg_settings, publish_event):

    global publish_data_counter, publish_data_limit

    current_timestamp = datetime.utcnow().isoformat()

    status_accel_payload = {
        "measurement": "Acceleration",
        "simulated": gsg_settings['simulated'],
        "runs_on": gsg_settings["runs_on"],
        "name": gsg_settings["name"],
        "accel": {
            "Ax": accel[0],
            "Ay": accel[1],
            "Az": accel[2],
        },
        "time": current_timestamp
    }

    status_gyro_payload = {
        "measurement": "Rotation",
        "simulated": gsg_settings['simulated'],
        "runs_on": gsg_settings["runs_on"],
        "name": gsg_settings["name"],
        "gyro": {
            "Gx": gyro[0],
            "Gy": gyro[1],
            "Gz": gyro[2],
        },
        "time": current_timestamp
    }

    with counter_lock:
        gsg_batch.append(('Acceleration', json.dumps(status_accel_payload), 0, True))
        gsg_batch.append(('Rotation', json.dumps(status_gyro_payload), 0, True))
        publish_data_counter += 1

    if publish_data_counter >= publish_data_limit:
        publish_event.set()

def run_gsg(settings, threads_list, output_queue):
        if settings['simulated']:
            gsg_simulator = GSGSimulator(output_queue, gsg_callback, settings, publish_event)
            gsg_simulator.start()
            threads_list.append(gsg_simulator)
        else:
            from sensors.gsg_sensor import GSG
            gsg = GSG(settings, output_queue, gsg_callback, publish_event)
            gsg.start()
            threads_list.append(gsg)
