import threading
import time
import random

def generate_values(initial_temp = 25, initial_humidity=20):
      temperature = initial_temp
      humidity = initial_humidity
      while True:
            temperature += random.uniform(-0.5, 0.5)  # Small random changes
            humidity += random.uniform(-1, 1)  # Moderate random changes

            # Ensure values are within valid ranges
            temperature = max(0, min(45, temperature))
            humidity = max(0, min(100, humidity))

            yield humidity, temperature

def generate_output(humidity, temperature, code):
    t = time.localtime()
    output = "="*20
    output += f"\nTimestamp: {time.strftime('%H:%M:%S', t)}\n"
    output += f"Code: {code}\n"
    output += f"Humidity: {humidity:.2f}%\n"
    output += f"Temperature: {temperature:.2f}°C\n"
    return output
            
class DHTSimulator(threading.Thread):
    def __init__(self, output_queue, callback, settings, publish_event):
        super().__init__()
        self.output_queue = output_queue
        self.running_flag = False
        self.callback = callback
        self.settings = settings
        self.publish_event = publish_event

    def run(self):
        while True:
            for humidity, temperature in generate_values(10, 30):
                if self.running_flag:
                    code = 0
                    time.sleep(1)
                    self.callback(humidity, temperature, self.settings, self.publish_event)
                    self.output_queue.put(generate_output(humidity, temperature, code))
                    