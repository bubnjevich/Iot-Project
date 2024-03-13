import threading
import time
import random
import paho.mqtt.client as mqtt
import json
from broker_settings import SERVER_IP
from datetime import datetime


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
        self.is_moving = False
    
    def simulate_gyroscope(self):
        stationary_gyro = lambda: random.uniform(-0.5, 0.5)
        movement_gyro = lambda: random.uniform(-90, 90)
        if self.is_moving:
            return [movement_gyro(), movement_gyro(), movement_gyro()]
        else:
            return [stationary_gyro(), stationary_gyro(), stationary_gyro()]

    def simulate_acceleration(self):
        stationary_accel = lambda: random.uniform(-0.1, 0.1)
        movement_accel = lambda: random.uniform(-2, 2)
        if self.is_moving:
            return [movement_accel(), movement_accel(), 9.81 + movement_accel()]
        else:
            return [stationary_accel(), stationary_accel(), 9.81]

    def handle_alarm(self, mqtt_client):
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
            self.is_moving = random.random() < 0.05
            gyro = self.simulate_gyroscope()
            accel = self.simulate_acceleration()
            if self.is_moving:
                self.handle_alarm( mqtt_client)
            output = generate_output(gyro, accel)
            self.output_queue.put(output)
            self.callback(accel, gyro, self.settings, self.publish_event)
            time.sleep(1)
            