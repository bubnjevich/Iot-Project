from simulators.pir_simulator import MotionSensorSimulator

def run_pir(settings, threads_list, output_queue):
        if settings['simulated']:
            pir_simulator = MotionSensorSimulator(output_queue)
            pir_simulator.start()
            threads_list.append(pir_simulator)
        else:
            from sensors.pir_sensor import PIRMotionSensor
            pir = PIRMotionSensor(settings['pin'], output_queue)
            pir.start()
            threads_list.append(pir)
