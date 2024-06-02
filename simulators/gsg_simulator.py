import threading
import time
import random
import paho.mqtt.client as mqtt
import json
from broker_settings import SERVER_IP
from datetime import datetime
import math

def generate_output(gyro, accel):
    t = time.localtime()
    output = "="*40
    output += f"\nTimestamp: {time.strftime('%H:%M:%S', t)}\n"
    output += "Rotation: " + f"({gyro[0]:.3f}, {gyro[1]:.3f}, {gyro[2]:.3f})\n"
    output += "Acceleration: " + f"({accel[0]:.3f}, {accel[1]:.3f}, {accel[2]:.3f})\n"
    return output


def runge_kutta_gyro_integration(gyro_data, dt):
    """
    Integracija podataka sa žiroskopa koristeći Runge-Kutta metodu četvrtog reda (RK4).
    :param gyro_data: Tuple (ωx, ωy, ωz) trenutni podaci sa žiroskopa
    :param dt: Vremenski interval između uzoraka
    :return: Tuple (delta_theta_x, delta_theta_y, delta_theta_z) - promene ugla rotacije u radijanima
    """
    omega_x, omega_y, omega_z = gyro_data

    k1_x, k1_y, k1_z = omega_x * dt, omega_y * dt, omega_z * dt
    k2_x, k2_y, k2_z = (omega_x + 0.5 * k1_x) * dt, (omega_y + 0.5 * k1_y) * dt, (omega_z + 0.5 * k1_z) * dt
    k3_x, k3_y, k3_z = (omega_x + 0.5 * k2_x) * dt, (omega_y + 0.5 * k2_y) * dt, (omega_z + 0.5 * k2_z) * dt
    k4_x, k4_y, k4_z = (omega_x + k3_x) * dt, (omega_y + k3_y) * dt, (omega_z + k3_z) * dt

    delta_theta_x = (1/6) * (k1_x + 2*k2_x + 2*k3_x + k4_x)
    delta_theta_y = (1/6) * (k1_y + 2*k2_y + 2*k3_y + k4_y)
    delta_theta_z = (1/6) * (k1_z + 2*k2_z + 2*k3_z + k4_z)

    return delta_theta_x, delta_theta_y, delta_theta_z

def rad_to_deg(rad):
    """Konverzija radijana u stepene"""
    return rad * (180.0 / math.pi)

class GSGSimulator(threading.Thread):
    def __init__(self, output_queue, callback, settings, publish_event):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = True
        self.callback = callback
        self.settings = settings
        self.publish_event = publish_event
        self.gyro_angles = [0, 0, 0]  # početni uglovi
        self.threshold_angle = 5.0
    
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

            gyro = self.simulate_gyroscope()
            accel = self.simulate_acceleration()

            dt = 1

            delta_theta_x, delta_theta_y, delta_theta_z = runge_kutta_gyro_integration(gyro, dt)
            self.gyro_angles[0] += delta_theta_x
            self.gyro_angles[1] += delta_theta_y
            self.gyro_angles[2] += delta_theta_z

            theta_x_deg = rad_to_deg(self.gyro_angles[0])
            theta_y_deg = rad_to_deg(self.gyro_angles[1])
            theta_z_deg = rad_to_deg(self.gyro_angles[2])

            if abs(theta_x_deg) >= self.threshold_angle or abs(theta_y_deg) >= self.threshold_angle or abs(
                    theta_z_deg) >= self.threshold_angle:
                self.handle_alarm(mqtt_client)

            output = generate_output(gyro, accel)
            self.output_queue.put(output)
            self.callback(accel, gyro, self.settings, self.publish_event)
            time.sleep(dt)
            