from simulators.dht_simulator import DHTSimulator



def run_dht(settings, threads_list, output_queue):
        if settings['simulated']:
            dht_simulator = DHTSimulator(output_queue)
            dht_simulator.start()
            threads_list.append(dht_simulator)
        else:
            from sensors.rdht_sensor import DHT
            dht_sensor = DHT(settings['pin'], output_queue)
            dht_sensor.start()
            threads_list.append(dht_sensor)
