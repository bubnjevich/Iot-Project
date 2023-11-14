import threading
import time
from simulators.ds_simulator import DoorSensorSimulator


def run_ds(settings, threads_list, output_queue):
        if settings['simulated']:
            ds_simulator = DoorSensorSimulator(output_queue)
            ds_simulator.start()
            threads_list.append(ds_simulator)
        else:
            from sensors.ds_sensor import Button
            ds = Button(settings['port'], output_queue)
            ds.start()
            threads_list.append(ds)
