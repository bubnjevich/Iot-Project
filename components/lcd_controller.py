from displays.lcd.glcd import LCD


def run_lcd(settings, threads_list, output_queue):
    if settings['simulated']:
        pass
    else:
        db = LCD()
        db.start()
        threads_list.append(db)
