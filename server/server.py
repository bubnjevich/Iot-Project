from datetime import datetime

from flask import Flask, jsonify, request
from influxdb_client import InfluxDBClient, Point
from flask_socketio import SocketIO, emit
from influxdb_client.client.write_api import SYNCHRONOUS
import paho.mqtt.client as mqtt
import json
import sched
import time
from congif import *


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")



# InfluxDB Configuration
token = ""
org = ""
with open(".env", "r") as file:
    for line in file:
        key, value = line.strip().split("=", 1)
        if key == "token": token = value
        if key == "org" : org = value

url = "http://localhost:8086" # influx
bucket = "example_db"

influxdb_client = InfluxDBClient(url=url, token=token, org=org)


# MQTT Configuration
mqtt_client = mqtt.Client() # serverski mqtt
mqtt_client.connect("localhost", 1883, 60) # radi preko dokera
mqtt_client.loop_start()
current_people_number = 0   # inicjalno nema nikoga u kuci



def on_connect(client, userdata, flags, rc):
    client.subscribe("Temperature")
    client.subscribe("Humidity")
    client.subscribe("Motion")
    client.subscribe("DoorStatus")
    client.subscribe("Distance")
    client.subscribe("MembraneSwitch")
    client.subscribe("Acceleration")
    client.subscribe("Rotation")
    client.subscribe("Alarm")
    client.subscribe("RPIR")
    client.subscribe("Light")
    client.subscribe("NotifyFrontend")
    client.subscribe("CurrentPeopleNumber") # sacuvaj trenutan broj ljudi


mqtt_client.on_connect = on_connect
mqtt_client.on_message = lambda client, userdata, msg: save_to_db(json.loads(msg.payload.decode('utf-8')))

def save_to_db(data):
    write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)

    if data["measurement"] == "Motion":
        handle_rpir_motion(data)
    if data["measurement"] == "Alarm":
        notify_possible_alarm(data)
    elif data["measurement"] == "Acceleration":
        point = handle_acceleration(data)
        write_api.write(bucket=bucket, org=org, record=point)
    elif data["measurement"] == "Rotation":
        point = handle_rotation(data)
        write_api.write(bucket=bucket, org=org, record=point)
    elif data["measurement"] == "NumberPeople":
        pass
    elif data["measurement"] == "Clock":
        # write_api.write(bucket=bucket, org=org, record=point)
        pass
    elif data["measurement"] == "NotifyFrontend":
        point = handle_alarm(data)
        write_api.write(bucket=bucket, org=org, record=point)

    else:
        point = handle_other_data(data)
        write_api.write(bucket=bucket, org=org, record=point)

def process_sensor(sensor_name):
    global current_people_number
    data_response = get_last_two_distance_of_dus(sensor_name)
    last = round(float(data_response["data"][0]["_value"]), 2)
    before_last = round(float(data_response["data"][1]["_value"]), 2)
    if last > before_last: # osoba izlazi iz objekta
        if current_people_number - 1 < 0:
            return
        
    current_people_number += 1 if last < before_last else -1
    print("Trenutan broj ljudi u kuci: ", current_people_number)
    handle_people()

def handle_rpir_motion(data):
    global current_people_number
    if data["value"] == 1:
        if data["name"] == "DB - MY_DPIR1":
            mqtt_client.publish("LIGHT_DL1")
            process_sensor("DUS1 - Device DUS")
        elif data["name"] == "Door Motion Sensor 2":
                process_sensor("Door Ultrasonic Sensor 2")
        elif data["name"].startswith("Room PIR"):
            # proveri brojno stanje ljudi u objektu ako je 0 izazovi alarm
            print("PRIMIO SAM PIR!")
            if current_people_number == 0:
                print("IZAZIVAM ALARM! NEKO SE MRDNUO!")
                send_alarm(data)




def send_alarm(data):
    current_timestamp = datetime.utcnow().isoformat()

    status_payload = {
        "measurement": "Alarm",
        "alarm_name": "RPIR Motion",
        "device_name": data["name"],
        "type": data["runs_on"],
        "start": 1,
        "time": current_timestamp
    }
    mqtt_client.publish("AlarmAlerted", json.dumps(status_payload))
    socketio.emit('alarm_detected', json.dumps(status_payload)) # TODO! samo ako je sistem aktivan



@socketio.on("PINInput")
def handle_pin_input(data):
    print("Primio sam PIN:", data)
    current_timestamp = datetime.utcnow().isoformat()
    point_data = {
        "measurement" : "DMS",
        "value" : str(data),
        "time": current_timestamp,
        "simulated" : False

    }
    mqtt_client.publish("AlarmAlerted", json.dumps(point_data))
    
    
@socketio.on("Clock")
def handle_clock_input(data):
    print("Sat navijen na: " , data)
    alarm_time = data['alarmTime']
    scheduler = sched.scheduler(time.time, time.sleep)
    alarm_timestamp = time.mktime(time.strptime(alarm_time, "%Y-%m-%dT%H:%M:%S"))
    
    def trigger_alarm():
        print("ALARM UGASEN!!")
        current_timestamp = datetime.utcnow().isoformat()
        point_data = {
            "measurement": "Clock",
            "value": data["isOn"],
            "time": current_timestamp,
            "simulated": False
            
        }
        mqtt_client.publish("Clock", json.dumps(point_data))
        
    
    scheduler.enterabs(alarm_timestamp, 1, trigger_alarm)
    scheduler.run()

def handle_alarm(data):
    # print("Alarm se gasi/pali jer je sistem aktivan....")
    # print(data)
    time = data["time"]
    status = "On" if data["start"] == 1 else "Off"
    global socketio
    point = (
        Point("Alarm")
        .tag("alarm_name", data["alarm_name"])
        .tag("device_name", data["device_name"])
        .tag("type", data["type"])
        .field("status", status)
        .time(time)
    )
    socketio.emit('alarm_detected', json.dumps(data))
    return point

    

def notify_possible_alarm(data):
    global socketio
    print("Primio sam upozorenje za alarm: ", data)
    mqtt_client.publish("AlarmAlerted", json.dumps(data))



def handle_people():
    current_timestamp = datetime.utcnow().isoformat()

    global current_people_number
    point = (
        Point("NumberPeople")
        .tag("name", "Number of people in the house")
        .time(current_timestamp)
        .field("measurement", current_people_number)
    )

    write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
    write_api.write(bucket=bucket, org=org, record=point)


def handle_acceleration(data): 
    time = data["time"]
    point = (
        Point(data["measurement"])
        .tag("simulated", data["simulated"])
        .tag("runs_on", data["runs_on"])
        .tag("name", data["name"])
        .time(time)
        .field("Ax", data["accel"]["Ax"])
        .field("Ay", data["accel"]["Ay"])
        .field("Az", data["accel"]["Az"])
    )
    return point

def handle_rotation(data):
    time = data["time"]
    point = (
        Point(data["measurement"])
        .tag("simulated", data["simulated"])
        .tag("runs_on", data["runs_on"])
        .tag("name", data["name"])
        .time(time)
        .field("Gx", data["gyro"]["Gx"])
        .field("Gy", data["gyro"]["Gy"])
        .field("Gz", data["gyro"]["Gz"])
    )
    return point

def handle_other_data(data):
    time = data["time"]
    point = (
        Point(data["measurement"])
        .tag("simulated", data["simulated"])
        .tag("runs_on", data["runs_on"])
        .tag("name", data["name"])
        .time(time)
        .field("measurement", data["value"])
    )
    return point

# Route to store dummy data
@app.route('/store_data', methods=['POST'])
def store_data():
    try:
        data = request.get_json()
        store_data(data)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


def handle_influx_query(query):
    with app.app_context():
        try:
            query_api = influxdb_client.query_api()
            tables = query_api.query(query, org=org)

            container = []
            for table in tables:
                for record in table.records:
                    container.append(record.values)

            return {
                "status" : "success",
                "data" : container
            }
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})


def get_last_two_distance_of_dus(dus_name):
    query = f"""
    from(bucket: "{bucket}")
      |> range(start: -2d)  
      |> filter(fn: (r) => r["_measurement"] == "Distance")
      |> filter(fn: (r) => r["name"] == "{dus_name}")
      |> sort(columns: ["_time"], desc: true)  
      |> limit(n: 2) 
      |> yield(name: "mean")
    """
    return handle_influx_query(query)


@app.route('/simple_query', methods=['GET'])
def retrieve_simple_data():
    query = f"""from(bucket: "{bucket}")
    |> range(start: -10m)
    |> filter(fn: (r) => r._measurement == "Humidity")"""
    return handle_influx_query(query)


@app.route('/aggregate_query', methods=['GET'])
def retrieve_aggregate_data():
    query = f"""from(bucket: "{bucket}")
    |> range(start: -10m)
    |> filter(fn: (r) => r._measurement == "Humidity")
    |> mean()"""
    return handle_influx_query(query)


@app.route('/dht', methods=['GET'])
def retrieve_dht_data():
    query = f"""
    
  from(bucket: "{bucket}")
  |> range(start: -6h)
  |> filter(fn: (r) => r["_measurement"] == "Humidity" or r["_measurement"] == "Temperature")
  |> mean()
  
  """
    return handle_influx_query(query)

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, use_reloader=False)  # Postavite odgovarajući port za soket konekciju
