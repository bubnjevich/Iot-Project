import threading
import time
from queue import Queue
import random
from configuration.configuration import load_settings
from components.rdht_controller import run_rdht
from components.dms_controller import run_dms
from components.dl_controller import run_dl
from components.ds_controller import run_ds

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
except:
    pass

def menu():
    print("\nIoT Device Menu:")
    print("1. Door Sensor (Button)")
    print("2. Door Light (LED diode)")
    print("3. Door Ultrasonic Sensor")
    print("4. Door Buzzer")
    print("5. Door Motion Sensor")
    print("6. Door Membrane Switch")
    print("7. Room PIR 1")
    print("8. Room PIR 2")
    print("9. Room DHT 1")
    print("10. Room DHT 2")
    choice = int(input("Enter the number of the IoT device (Ctrl+C to exit): "))
    return choice

def start_threads(thread_list, output_queue, settings):
    ds1_settings = settings['DS1']
    dl_settings = settings['DL']
    dms_settings = settings['DMS']
    rdht1_settings = settings['RDHT1']
    rdht2_settings = settings['RDHT2']

    run_ds(ds1_settings, thread_list, output_queue)
    run_dl(dl_settings, thread_list, output_queue)
    run_dms(dms_settings, thread_list, output_queue)
    run_rdht(rdht1_settings, thread_list, output_queue)
    run_rdht(rdht2_settings, thread_list, output_queue)




def main():
    output_queue = Queue()
    settings = load_settings()
    thread_list = []

    start_threads(thread_list, output_queue, settings)
    menu_flag = True
    
    while True:
        try:
            if menu_flag:
                choice = menu()
                if choice < 1 or choice > 11:
                    print("Invalid choice!")
                else:
                    selected_thread = thread_list[choice - 1]
                    selected_thread.running_flag = True
                    menu_flag = False
            else:
                output = output_queue.get()
                print(output)
        except KeyboardInterrupt:
            menu_flag = True
            while not output_queue.empty():
                output = output_queue.get()
            for thread in thread_list:
                thread.running_flag = False

if __name__ == "__main__":
    main()
