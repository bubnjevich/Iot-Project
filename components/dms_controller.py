import threading
import time
from simulators.dms_simulator import DoorMembraneSwitchSimulator


def run_dms(settings, threads_list, output_queue):
        if settings['simulated']:
            dms_simulator = DoorMembraneSwitchSimulator(output_queue)
            dms_simulator.start()
            threads_list.append(dms_simulator)
        else:
            from sensors.dms_sensor import MembraneKeypad
            dms = MembraneKeypad(settings, output_queue)
            dms.start()
            threads_list.append(dms)
