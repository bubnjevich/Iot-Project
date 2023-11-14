from simulators.dht_simulator import DHTSimulator
import threading
import time


def run_rdht(settings, threads_list, output_queue):
        if settings['simulated']:
            rdht_simulator = DHTSimulator(output_queue)
            rdht_simulator.start()
            threads_list.append(rdht_simulator)
        else:
            from sensors.rdht_sensor import DHT
            rdht_sensor = DHT(settings['pin'], output_queue)
            rdht_sensor.start()
            threads_list.append(rdht_sensor)
