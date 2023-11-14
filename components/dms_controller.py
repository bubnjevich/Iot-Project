import threading
import time
from simulators.dms_simulator import DoorMembraneSwitchSimulator


def run_dms(settings, threads_list, output_queue):
        if settings['simulated']:
            dms_simulator = DoorMembraneSwitchSimulator(output_queue)
            dms_simulator.start()
            threads_list.append(dms_simulator)
        else:
            from sensors.rdht1_sensor import run_dht_loop, DHT
            print("Starting dht1 loop")
            rdht1 = DHT(settings['pin'])
            rdht1_thread = threading.Thread(target=run_dht_loop, args=(rdht1, 2, dht_callback, stop_event))
            rdht1_thread.start()
            threads_list.append(rdht1_thread)
            print("Dht1 loop started")
