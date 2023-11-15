import threading
from simulators.dl_simulator import DoorLightSimulator

def run_dl(settings, threads_list, output_queue):
        if settings['simulated']:
            dl_simulator = DoorLightSimulator(output_queue)
            dl_simulator.start()
            threads_list.append(dl_simulator)
        else:
            from actuators.dl import LED
            dl = LED(settings['port'], output_queue)
            dl.start()
            threads_list.append(dl)
