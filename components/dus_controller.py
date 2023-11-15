from simulators.dus_simulator import DoorUltrasonicSensorSimulator


def run_dus(settings, threads_list, output_queue):
        if settings['simulated']:
            dus1_simulator = DoorUltrasonicSensorSimulator(output_queue)
            dus1_simulator.start()
            threads_list.append(dus1_simulator)
        else:
            from sensors.dus_sensor import UltrasonicDistanceSensor
            dus = DoorUltrasonicSensorSimulator(settings["TRIG_PIN"], settings["ECHO_PIN"], output_queue)
            dus.start()
            threads_list.append(dus)
