from displays.d4s7.four_segment import D4S7
from simulators.four_segment_simulator import FourSegmentSimulator

def run_four_sd(settings, threads_list, output_queue):

    if settings['simulated']:
        db = FourSegmentSimulator(output_queue)
        db.start()
        threads_list.append(db)
    else:
        db = D4S7()
        db.start()
        threads_list.append(db)
