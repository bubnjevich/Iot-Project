from simulators.db_simulator import DoorBuzzerSimulator


def run_db(settings, threads_list, output_queue):
        if settings['simulated']:
            db_simulator = DoorBuzzerSimulator(output_queue)
            db_simulator.start()
            threads_list.append(db_simulator)
        else:
            from actuators.db import Buzzer
            db = Buzzer(settings['pin'])
            db.start()
            threads_list.append(db)
