import threading
from gsg import MPU6050
import time
import os


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


    def setup(self):
        self.mpu.dmp_initialize()


    def run(self) -> None:
        self.setup()
        while True:
            if self.running_flag:
                accel = self.mpu.get_acceleration()  # get accelerometer data
                gyro = self.mpu.get_rotation()  # get gyroscope data
                os.system('clear')
                #TODO:
                # print("a/g:%d\t%d\t%d\t%d\t%d\t%d " % (accel[0], accel[1], accel[2], gyro[0], gyro[1], gyro[2]))
                # print("a/g:%.2f g\t%.2f g\t%.2f g\t%.2f d/s\t%.2f d/s\t%.2f d/s" % (accel[0] / 16384.0, accel[1] / 16384.0,
                #                                                                     accel[2] / 16384.0, gyro[0] / 131.0,
                #                                                                     gyro[1] / 131.0, gyro[2] / 131.0))
                time.sleep(0.1)

