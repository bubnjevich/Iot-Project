from lcd.glcd import LCD

def send_dht(temperature, humidity):
    pass


def run_lcd(settings, threads_list, output_queue):
    if settings['simulated']:
        pass
    else:
        db = LCD()
        db.start()
        threads_list.append(db)
