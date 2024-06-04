import threading
import time
from displays.lcd.PCF8574 import PCF8574_GPIO
from displays.lcd.Adafruit_LCD1602 import Adafruit_CharLCD
from broker_settings import SERVER_IP
import json

import paho.mqtt.client as mqtt

class LCD(threading.Thread):

    def __init__(self):
        super().__init__()
        self.mcp = None
        self.lcd = None
        self.temperature = ""
        self.humidity = ""

    def setup(self):
        PCF8574_address = 0x27  # I2C address of the PCF8574 chip.
        PCF8574A_address = 0x3F  # I2C address of the PCF8574A chip.
        # Create PCF8574 GPIO adapter.
        try:
            self.mcp = PCF8574_GPIO(PCF8574_address)
        except:
            try:
                self.mcp = PCF8574_GPIO(PCF8574A_address)
            except:
                print('I2C Address Error !')
                exit(1)
        # Create LCD, passing in MCP GPIO adapter.
        self.lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4, 5, 6, 7], GPIO=self.mcp)

    def destroy(self):
        self.lcd.clear()
        self.mcp.output(3, 1)  # turn on LCD backlight
        self.lcd.begin(16, 2)  # set number of LCD lines and columns


    def handle_gdht(self, data):
        if data["measurement"] == "Temperature":
            self.temperature = str(data["value"]) + "C"
        elif data["measurement"] == "Humidity":
            self.humidity = str(data["value"]) + "%"


    def run(self) -> None:
        self.setup()
        mqtt_client = mqtt.Client()
        mqtt_client.connect(SERVER_IP, 1883, 60)
        mqtt_client.loop_start()
        mqtt_client.subscribe("GDHT")
        mqtt_client.on_message = lambda client, userdata, message: self.handle_gdht(json.loads(message.payload.decode('utf-8')))

        while True:
            # lcd.clear()

            self.lcd.setCursor(0, 0)  # set cursor position
            self.lcd.message('T: ' + self.temperature + '\n')  # display CPU temperature
            self.lcd.message('H: ' + self.humidity)  # display the time
            # KZI315, Stigoperadononet
            # GDHT+GLCD;
            time.sleep(1)