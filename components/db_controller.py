from simulators.db_simulator import DoorBuzzerSimulator
from datetime import datetime
import json
import paho.mqtt.publish as publish
from broker_settings import HOSTNAME, PORT, SERVER_IP
import threading

db_batch = []
publish_data_counter = 0
publish_data_limit = 5
counter_lock = threading.Lock()

def publisher_task(event, db_batch):
    global publish_data_counter, publish_data_limit
    while True:
        event.wait()
        with counter_lock:
            local_dht_batch = db_batch.copy()
            publish_data_counter = 0
            db_batch.clear()
        publish.multiple(local_dht_batch, hostname=SERVER_IP, port=PORT)
        #print(f'published {publish_data_limit} db values')
        event.clear()

publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, db_batch,))
publisher_thread.daemon = True
publisher_thread.start()

def db_callback(buzz,db_settings, publish_event):
    global publish_data_counter, publish_data_limit

    # Current timestamp
    current_timestamp = datetime.utcnow().isoformat()
    
    humidity_payload = {
        "measurement": "Buzzer",
        "simulated": db_settings['simulated'],
        "runs_on": db_settings["runs_on"],
        "name": db_settings["name"],
        "value": buzz,
        "time": current_timestamp
    }

    with counter_lock:
        db_batch.append(('Buzzer', json.dumps(humidity_payload), 0, True))
        publish_data_counter += 1

    if publish_data_counter >= publish_data_limit:
        publish_event.set()



def run_db(settings, threads_list, output_queue):
        if settings['simulated']:
            db_simulator = DoorBuzzerSimulator(output_queue, db_callback, settings, publish_event)
            db_simulator.start()
            threads_list.append(db_simulator)
        else:
            from actuators.db import Buzzer
            db = Buzzer(settings['pin'], db_callback, settings, publish_event)
            db.start()
            threads_list.append(db)
