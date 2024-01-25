import threading
from gsg import MPU6050
import time
import os
import paho.mqtt.client as mqtt
from broker_settings import HOSTNAME
from datetime import datetime


class GSG(threading.Thread):
    def __init__(self, settings, output_queue, callback, publish_event):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = True
        self.callback = callback
        self.publish_event = publish_event
        self.settings = settings
        self.mpu = MPU6050.MPU6050()  # instantiate a MPU6050 class object
        self.accel = [0] * 3  # store accelerometer data
        self.gyro = [0] * 3  # store gyroscope data
        self.prev_accel = [0, 0, 0]
        self.significant_accel_change = 0.5  # Define what you consider significant (in g's)
        self.significant_gyro_change = 50.0 
        self.prev_gyro = [0, 0, 0]


    def setup(self):
        self.mpu.dmp_initialize()

    def is_significant_change(self, current, previous, threshold):
        return any(abs(c - p) > threshold for c, p in zip(current, previous))
    
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
        mqtt_client.publish("Alarm", status_payload)


    def run(self) -> None:
        self.setup()
        mqtt_client = mqtt.Client()
        mqtt_client.connect(HOSTNAME, 1883, 60)
        mqtt_client.loop_start()
        while True:
            if self.running_flag:
                current_accel = self.mpu.get_acceleration()
                current_gyro = self.mpu.get_rotation()
                if self.is_significant_change(current_accel, self.prev_accel, self.significant_accel_change):
                    self.handle_alarm( mqtt_client)
                    print("Significant acceleration change detected!")
                if self.is_significant_change(current_gyro, self.prev_gyro, self.significant_gyro_change):
                    self.handle_alarm( mqtt_client)
                    print("Significant gyro change detected!")
                self.prev_accel = current_accel
                self.prev_gyro = current_gyro
                self.callback(current_accel, current_gyro, self.settings, self.publish_event)
                os.system('clear')
                time.sleep(0.1)

