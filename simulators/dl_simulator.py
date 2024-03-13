import threading
import time
import paho.mqtt.client as mqtt
from broker_settings import SERVER_IP

class DoorLightSimulator(threading.Thread):
    def __init__(self, output_queue, callback, settings, publish_event):
        super().__init__()
        self.running_flag = True
        self.state = False
        self.output_queue = output_queue
        self.callback = callback
        self.settings = settings
        self.publish_event = publish_event
    
    def toggle_light(self):
        self.state = True
        time.sleep(10)
        self.state = False

    def run(self):
        mqtt_client = mqtt.Client()
        mqtt_client.connect(SERVER_IP, 1883, 60) # prima poruku od servera da treba da upali svetlo jer se desio pokret na DPIR1
        mqtt_client.loop_start()
        mqtt_client.subscribe("LIGHT_DL1")
        mqtt_client.on_message = lambda client, userdata, message: self.toggle_light()
    
        while True:
            if self.running_flag:
                state = 1 if self.state else 0 # na svakih 5 sekundi pise u bazu stanje svetla
                self.output_queue.put(f"Current Door Light State: {state}")
                self.callback(state, self.settings, self.publish_event)
                time.sleep(5)
