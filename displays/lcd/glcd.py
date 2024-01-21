import threading
import time
from typing import Any
from displays.lcd.PCF8574 import PCF8574_GPIO
from displays.lcd.Adafruit_LCD1602 import Adafruit_CharLCD

class LCD(threading.Thread):

    def __init__(self):
        super().__init__()
        self.mcp = None
        self.lcd = None


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


    def run(self) -> None:
        self.setup()
        while True:
            # lcd.clear()
            self.lcd.setCursor(0, 0)  # set cursor position
            # TODO: posalji dht na izlaz
            #  self.lcd.message('CPU: ' + get_cpu_temp() + '\n')  # display CPU temperature
            #  self.lcd.message(get_time_now())  # display the time
            time.sleep(1)