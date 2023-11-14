import threading
import time
from queue import Queue
import random
from configuration.configuration import load_settings
from components.rdht1_controller import run_rdht1
from components.dms_controller import run_dms



try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
except:
    pass


class DoorMembraneSwitchSimulator(threading.Thread):
    def __init__(self, output_queue):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = False

    def run(self):
        while True:
            if self.running_flag:
                value = random.choice(['A', 'B', 'C', 'D', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '*', '#'])
                self.output_queue.put(f"Value: {value}")
                time.sleep(1)

class DoorSensorSimulator(threading.Thread):
    def __init__(self, output_queue):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = False

    def run(self):
        while True:
            if self.running_flag:
                status = random.choice(['Open', 'Closed'])
                self.output_queue.put(f"Door Sensor Status: {status}")
                time.sleep(1)

class DoorLightSimulator(threading.Thread):
    def __init__(self, output_queue):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = False

    def run(self):
        while True:
            if self.running_flag:
                state = random.choice(['On', 'Off'])
                self.output_queue.put(f"Door Light State: {state}")
                time.sleep(1)

class DoorUltrasonicSensorSimulator(threading.Thread):
    def __init__(self, output_queue):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = False

    def run(self):
        while True:
            if self.running_flag:
                distance = round(random.uniform(1, 100), 2)
                self.output_queue.put(f"Door Ultrasonic Sensor Distance: {distance} cm")
                time.sleep(1)

class DoorBuzzerSimulator(threading.Thread):
    def __init__(self, output_queue):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = False

    def run(self):
        while True:
            if self.running_flag:
                sound = random.choice(['On', 'Off'])
                self.output_queue.put(f"Door Buzzer State: {sound}")
                time.sleep(1)

class DoorMotionSensorSimulator(threading.Thread):
    def __init__(self, output_queue):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = False

    def run(self):
        while True:
            if self.running_flag:
                motion = random.choice(['Detected', 'Not Detected'])
                self.output_queue.put(f"Door Motion Sensor Status: {motion}")
                time.sleep(1)

class RoomPIRSimulator(threading.Thread):
    def __init__(self, output_queue):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = False

    def run(self):
        while True:
            if self.running_flag:
                motion = random.choice(['Detected', 'Not Detected'])
                self.output_queue.put(f"Room PIR Status: {motion}")
                time.sleep(1)

class RoomDHTSimulator(threading.Thread):
    def __init__(self, output_queue):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = False

    def run(self):
        while True:
            if self.running_flag:
                temperature = round(20 + 10 * (1 - 2 * time.time() % 2), 2)
                humidity = round(50 + 20 * (1 - 2 * time.time() % 2), 2)
                self.output_queue.put(f"Room DHT - Temperature: {temperature}°C, Humidity: {humidity}%")
                time.sleep(1)

def main():
    output_queue = Queue()
    settings = load_settings()
    thread_list = []

    rdht1_settings = settings['RDHT1']
    dms_settings = settings['DMS']
    run_rdht1(rdht1_settings, thread_list, output_queue)
    run_dms(dms_settings, thread_list, output_queue)
    
    door_switch_simulator = DoorMembraneSwitchSimulator(output_queue)
    door_sensor_simulator = DoorSensorSimulator(output_queue)
    door_light_simulator = DoorLightSimulator(output_queue)
    door_ultrasonic_simulator = DoorUltrasonicSensorSimulator(output_queue)
    door_buzzer_simulator = DoorBuzzerSimulator(output_queue)
    room_pir_simulator = RoomPIRSimulator(output_queue)
    room_dht_simulator = RoomDHTSimulator(output_queue)

    door_switch_simulator.start()
    door_sensor_simulator.start()
    door_light_simulator.start()
    door_ultrasonic_simulator.start()
    door_buzzer_simulator.start()
    room_pir_simulator.start()
    room_dht_simulator.start()

    thread_list.extend([ door_switch_simulator, door_sensor_simulator, door_light_simulator,
                        door_ultrasonic_simulator, door_buzzer_simulator,
                        room_pir_simulator, room_dht_simulator])

    menu_flag = True
    
    while True:
        try:
            if menu_flag:
                print("\nIoT Device Menu:")
                print("1. DHT (Temperature and Humidity)")
                print("2. Door Membrane Switch")
                print("3. Door Sensor (Button)")
                print("4. Door Light (LED diode)")
                print("5. Door Ultrasonic Sensor")
                print("6. Door Buzzer")
                print("7. Door Motion Sensor")
                print("8. Room PIR")
                print("9. Room DHT")
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
