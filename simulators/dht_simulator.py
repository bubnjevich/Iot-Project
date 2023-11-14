import threading
import time
import random

def generate_values(initial_temp = 25, initial_humidity=20):
      temperature = initial_temp
      humidity = initial_humidity
      while True:
            temperature = temperature + random.randint(-1, 1)
            humidity = humidity + random.randint(-1, 1)
            if humidity < 0:
                  humidity = 0
            if humidity > 100:
                  humidity = 100
            yield humidity, temperature

def generate_output(humidity, temperature, code):
    t = time.localtime()
    output = "="*20
    output += f"\nTimestamp: {time.strftime('%H:%M:%S', t)}\n"
    output += f"Code: {code}\n"
    output += f"Humidity: {humidity}%\n"
    output += f"Temperature: {temperature}°C\n"
    return output
            
class DHTSimulator(threading.Thread):
    def __init__(self, output_queue):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = False

    def run(self):
        while True:
            for humidity, temperature in generate_values():
                if self.running_flag:
                    code = 100
                    self.output_queue.put(generate_output(humidity, temperature, code))
                    time.sleep(1)
              