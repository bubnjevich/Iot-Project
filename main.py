import threading
import time
from queue import Queue
import random


class DHTSimulator(threading.Thread):
    def __init__(self, output_queue):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = False

    def run(self):
        while True:
            if self.running_flag:
                temperature = round(20 + 10 * (1 - 2 * time.time() % 2), 2)
                humidity = round(50 + 20 * (1 - 2 * time.time() % 2), 2)
                self.output_queue.put(f"Temperature: {temperature}°C, Humidity: {humidity}%")
                time.sleep(1)

class DoorMembraneSwitchSimulator(threading.Thread):
    def __init__(self, output_queue):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = False


    def run(self):
        while True:
            if self.running_flag:
                value = random.choice(['A', 'B', 'C', 'D', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
                self.output_queue.put(f"Value: {value}")
                time.sleep(1)

def main():
    output_queue = Queue()
    thread_list = []

    dht_simulator = DHTSimulator(output_queue)
    door_switch_simulator = DoorMembraneSwitchSimulator(output_queue)

    dht_simulator.start()
    door_switch_simulator.start()
    thread_list.append(dht_simulator)
    thread_list.append(door_switch_simulator)

    menu_flag = True
    

    while True:
        try:
            if menu_flag:
                print("IoT Device Menu:")
                print("1. DHT (Temperature and Humidity)")
                print("2. Door Membrane Switch")

                choice = int(input("Enter the number of the IoT device (Ctrl+C to exit): "))
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
