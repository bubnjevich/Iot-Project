from flask import Flask, jsonify, request
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import paho.mqtt.client as mqtt
import json


app = Flask(__name__)


# InfluxDB Configuration
token = ""
org = ""
with open(".env", "r") as file:
    for line in file:
        key, value = line.strip().split("=", 1)
        if key == "token": token = value
        if key == "org" : org = value

url = "http://localhost:8086"
bucket = "example_db"

influxdb_client = InfluxDBClient(url=url, token=token, org=org)


# MQTT Configuration
mqtt_client = mqtt.Client()
mqtt_client.connect("localhost", 1883, 60)
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
    client.subscribe("CurrentPeopleNumber") # sacuvaj trenutan broj ljudi


mqtt_client.on_connect = on_connect
mqtt_client.on_message = lambda client, userdata, msg: save_to_db(json.loads(msg.payload.decode('utf-8')))


def save_to_db(data):
    write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
    if data["measurement"] == "Alarm":
        point = handle_alarms(data)
        write_api.write(bucket=bucket, org=org, record=point)
    elif data["measurement"] == "Acceleration":
        point = handle_acceleration(data)
        write_api.write(bucket=bucket, org=org, record=point)
    elif data["measurement"] == "Rotation":
        point = handle_rotation(data)
        write_api.write(bucket=bucket, org=org, record=point)
    elif data["measurement"] == "NumberPeople":
        point = handle_people(data)
        write_api.write(bucket=bucket, org=org, record=point)
    else:
        point = handle_other_data(data)
        write_api.write(bucket=bucket, org=org, record=point)

        
def handle_alarms(data):
    time = data["time"]
    point = (
        Point(data["measurement"])
        .tag("alarm_name", data["simulated"])
        .tag("device_name", data["device_name"])
        .tag("type", data["type"])
        .field("start", data["start"])
        .time(time)
    )
    return point

def handle_people(data):
    time = data["time"]
    global current_people_number
    if not (int(data["value"]) < 0 and current_people_number <= 0):
        current_people_number += int(data["value"])
    point = (
        Point(data["measurement"])
        .tag("name", "Number of people in the house")
        .time(time)
        .field("measurement", current_people_number)
    )
    return point

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
    try:
        query_api = influxdb_client.query_api()
        tables = query_api.query(query, org=org)

        container = []
        for table in tables:
            for record in table.records:
                container.append(record.values)

        return jsonify({"status": "success", "data": container})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


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
    app.run(debug=True)
