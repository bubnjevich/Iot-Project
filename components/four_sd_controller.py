from displays.d4s7.four_segment import D4S7

def run_4sd(settings, threads_list, output_queue):

    if settings['simulated']:
        pass
    else:
        db = D4S7()
        db.start()
        threads_list.append(db)
