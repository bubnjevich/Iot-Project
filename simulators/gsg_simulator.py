import threading
import time
import random

import numpy as np
import paho.mqtt.client as mqtt
import json
from broker_settings import SERVER_IP
from datetime import datetime
from rk4_utils import rk4


def generate_output(gyro, accel):
    t = time.localtime()
    output = "="*40
    output += f"\nTimestamp: {time.strftime('%H:%M:%S', t)}\n"
    output += "Rotation: " + f"({gyro[0]:.3f}, {gyro[1]:.3f}, {gyro[2]:.3f})\n"
    output += "Acceleration: " + f"({accel[0]:.3f}, {accel[1]:.3f}, {accel[2]:.3f})\n"
    return output

class GSGSimulator(threading.Thread):
    def __init__(self, output_queue, callback, settings, publish_event):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = True
        self.callback = callback
        self.settings = settings
        self.publish_event = publish_event
        self.gyro_angles = [0, 0, 0]  # početni uglovi
        self.threshold_angle = 0.55
        self.is_moving = False

        self.MOVEMENT_PROBABILITY = 0.05
        self.THRESHOLD_ANGLE = 10.0
    
    def simulate_gyroscope(self):
        noise_level = 0.01
        stationary_gyro = lambda: random.uniform(-0.5, 0.5)
        movement_gyro = lambda: random.uniform(-90, 90)
        if self.is_moving:
            return [movement_gyro() + random.uniform(-noise_level, noise_level) for _ in range(3)]
        else:
            return [stationary_gyro() + random.uniform(-noise_level, noise_level) for _ in range(3)]

    def simulate_acceleration(self):
        noise_level = 0.01
        stationary_accel = lambda: random.uniform(-0.1, 0.1)
        movement_accel = lambda: random.uniform(-2, 2)
        if self.is_moving:
            return [movement_accel() + random.uniform(-noise_level, noise_level) for _ in range(2)] + [
                9.81 + movement_accel() + random.uniform(-noise_level, noise_level)]
        else:
            return [stationary_accel() + random.uniform(-noise_level, noise_level) for _ in range(2)] + [
                9.81 + random.uniform(-noise_level, noise_level)]

    def handle_alarm(self, mqtt_client):
        print("detektujem znacajn POMERAJ!!!")
        current_timestamp = datetime.utcnow().isoformat()
        status_payload = {
            "measurement": "Alarm",
            "alarm_name": "Gyroscope " + self.settings["runs_on"],
            "device_name" : self.settings["name"],
            "type": "DS" + self.settings["runs_on"],
            "start" : 1,
            "time" : current_timestamp
        }
        mqtt_client.publish("Alarm", json.dumps(status_payload))

    def run(self):
        mqtt_client = mqtt.Client()
        mqtt_client.connect(SERVER_IP, 1883, 60)
        mqtt_client.loop_start()
        while True:
            if random.random() < self.MOVEMENT_PROBABILITY:
                self.is_moving = True
            else:
                self.is_moving = False
            gyro = self.simulate_gyroscope()
            accel = self.simulate_acceleration()

            dt = 1
            dqn = rk4(np.array(self.gyro_angles), gyro, dt)  # Convert to numpy array
            print(dqn)

            self.gyro_angles = gyro  # Convert back to list for consistency
            if max(abs(angle) for angle in dqn[1:]) > self.threshold_angle:
                self.handle_alarm(mqtt_client)
            output = generate_output(gyro, accel)
            self.output_queue.put(output)
            self.callback(accel, gyro, self.settings, self.publish_event)
            time.sleep(dt)
            