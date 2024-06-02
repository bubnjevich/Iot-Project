import threading
import time
try:
	import RPi.GPIO as GPIO
except:
	pass

class DHT(threading.Thread):
	DHTLIB_OK = 0
	DHTLIB_ERROR_CHECKSUM = -1
	DHTLIB_ERROR_TIMEOUT = -2
	DHTLIB_INVALID_VALUE = -999
	
	DHTLIB_DHT11_WAKEUP = 0.020#0.018		#18ms
	DHTLIB_TIMEOUT = 0.0001			#100us
	
	humidity = 0
	temperature = 0
	
	def __init__(self, pin, output_queue, callback, settings, publish_event):
		super().__init__()
		self.pin = pin
		self.settings = settings
		self.bits = [0,0,0,0,0]
		self.output_queue = output_queue
		self.running_flag = True
		self.callback = callback
		self.publish_event = publish_event


	#Read DHT sensor, store the original data in bits[]	
	def readSensor(self,pin,wakeupDelay):
		mask = 0x80
		idx = 0
		self.bits = [0,0,0,0,0]
		GPIO.setup(pin,GPIO.OUT)
		GPIO.output(pin,GPIO.LOW)
		time.sleep(wakeupDelay)
		GPIO.output(pin,GPIO.HIGH)
		#time.sleep(40*0.000001)
		GPIO.setup(pin,GPIO.IN)
		
		loopCnt = self.DHTLIB_TIMEOUT
		t = time.time()
		while(GPIO.input(pin) == GPIO.LOW):
			if((time.time() - t) > loopCnt):
				#print ("Echo LOW")
				return self.DHTLIB_ERROR_TIMEOUT
		t = time.time()
		while(GPIO.input(pin) == GPIO.HIGH):
			if((time.time() - t) > loopCnt):
				#print ("Echo HIGH")
				return self.DHTLIB_ERROR_TIMEOUT
		for i in range(0,40,1):
			t = time.time()
			while(GPIO.input(pin) == GPIO.LOW):
				if((time.time() - t) > loopCnt):
					#print ("Data Low %d"%(i))
					return self.DHTLIB_ERROR_TIMEOUT
			t = time.time()
			while(GPIO.input(pin) == GPIO.HIGH):
				if((time.time() - t) > loopCnt):
					#print ("Data HIGH %d"%(i))
					return self.DHTLIB_ERROR_TIMEOUT		
			if((time.time() - t) > 0.00005):	
				self.bits[idx] |= mask
			#print("t : %f"%(time.time()-t))
			mask >>= 1
			if(mask == 0):
				mask = 0x80
				idx += 1	
		#print (self.bits)
		GPIO.setup(pin,GPIO.OUT)
		GPIO.output(pin,GPIO.HIGH)
		return self.DHTLIB_OK
	#Read DHT sensor, analyze the data of temperature and humidity
	def readDHT11(self):
		rv = self.readSensor(self.pin,self.DHTLIB_DHT11_WAKEUP)
		if (rv is not self.DHTLIB_OK):
			self.humidity = self.DHTLIB_INVALID_VALUE
			self.temperature = self.DHTLIB_INVALID_VALUE
			return rv
		self.humidity = self.bits[0]
		self.temperature = self.bits[2] + self.bits[3]*0.1
		sumChk = ((self.bits[0] + self.bits[1] + self.bits[2] + self.bits[3]) & 0xFF)
		if(self.bits[4] is not sumChk):
			return self.DHTLIB_ERROR_CHECKSUM
		return self.DHTLIB_OK
	def run(self):
		while True:
			check = self.readDHT11()
			code = parseCheckCode(check)
			if self.running_flag:
				self.output_queue.put(generate_output(self.humidity, self.temperature, self.settings["name"]))
				self.callback(self.humidity, self.temperature, self.settings, self.publish_event)
			time.sleep(1)
		
def parseCheckCode(code):
	if code == 0:
		return "DHTLIB_OK"
	elif code == -1:
		return "DHTLIB_ERROR_CHECKSUM"
	elif code == -2:
		return "DHTLIB_ERROR_TIMEOUT"
	elif code == -999:
		return "DHTLIB_INVALID_VALUE"

def generate_output(humidity, temperature, code):
    t = time.localtime()
    output = "="*20
    output += f"\nTimestamp: {time.strftime('%H:%M:%S', t)}\n"
    output += f"Code: {code}\n"
    output += f"Humidity: {humidity}%\n"
    output += f"Temperature: {temperature}°C\n"
    return output

