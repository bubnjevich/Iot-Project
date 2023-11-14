import threading
import time

class DoorLightSimulator(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running_flag = False
        self.state = False

    def run(self):
        while True:
            if self.running_flag:
                state = "ON"
                if self.state == False:
                    state = "OFF"
                print(f"Current Door Light State: {state}")
                new_state = input("Enter New Door Light State (on/off): ")
                if(new_state.upper() == "ON"):
                    self.state = True
                elif(new_state.upper() == "OFF"):
                    self.state = False
                time.sleep(1)

