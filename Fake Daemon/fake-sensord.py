from typing import TypedDict, Any
from pathlib import Path
from paho.mqtt.client import Client
from tqdm import tqdm
import json
import time
import argparse

class DataPoint(TypedDict):
    timestamp: float
    id: str
    data: Any

def run(data_dir, mqtt_server, mqtt_port, seek, stop, speed, keep_timestamps):
    datapoints: list[DataPoint] = []

    print("Loading data")
    for file in data_dir.iterdir():
        if file.name.endswith(".ndjson"):
            print(f"    {file.name} - ", end="")
            id = file.name.removesuffix(".ndjson")
            
            total_datapoints = 0
            this_datapoints = []

            with open(file, "rb") as file:
                for line in file:
                    line = line.strip()
                    parsed = json.loads(line)

                    total_datapoints += 1

                    if seek != None and parsed["timestamp"] < seek:
                        continue

                    if stop != None and parsed["timestamp"] > stop:
                        continue

                    this_datapoints.append({
                        "id": id,
                        "timestamp": parsed["timestamp"],
                        "data": parsed
                    })

            if seek != None or stop != None:
                print(f"{len(this_datapoints)}/{total_datapoints} datapoints")
            else:
                print(f"{len(this_datapoints)} datapoints")

            datapoints += this_datapoints

    datapoints.sort(key=lambda x: x["timestamp"])
    print(f"Timestamps range from {datapoints[0]['timestamp']} to {datapoints[-1]['timestamp']}")

    print(f"Connecting to broker ({mqtt_server}:{mqtt_port})")
    client = Client(client_id="fake-sensord", clean_session=True)
    client.connect(mqtt_server, mqtt_port)
    client.loop_start()

    start_time = time.time()
    publish_time_offset = start_time - datapoints[0]['timestamp']
    for datapoint in tqdm(datapoints, "Sending packets", unit=" packets"):
        # When speed is not 1, this simulates the clock running slow/fast
        # When speed is 1 (default), this is the same as just time.time()
        now = start_time + ((time.time() - start_time) * speed)
        
        publish_timestamp = datapoint["timestamp"] + publish_time_offset

        if not keep_timestamps:
            # Adjust update timestamps in published packets, if requested
            datapoint["data"]["timestamp"] = publish_timestamp

        if now < publish_timestamp:
            time.sleep(publish_timestamp - now)

        client.publish(f"sensors/{datapoint['id']}", json.dumps(datapoint["data"]))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog = 'fake-sensord',
        description = 'Fake sensor daemon that publishes JSON sensor data to an MQTT broker')
    
    parser.add_argument("--data-dir", help="Folder containing .ndjson files", type=Path, required=True)
    parser.add_argument("--mqtt-server", help="MQTT server to connect to", default="127.0.0.1")
    parser.add_argument("--mqtt-port", help="MQTT port", type=int, default=1883)
    parser.add_argument("--seek", help="Immediately skip to this timestamp", type=int, default=None)
    parser.add_argument("--stop", help="Stop sending at this timestamp", type=int, default=None)
    parser.add_argument("--speed", help="Relative speed to transmit at", type=float, default=1.0)
    parser.add_argument("--keep-timestamps", help="Keep original timestamps instead of shifting them to the current time", action='store_true')

    args = parser.parse_args()
    run(**vars(args))
