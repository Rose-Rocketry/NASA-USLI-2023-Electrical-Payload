from threading import Thread
from time import sleep
from importlib import import_module
import logging
import sys
import paho.mqtt.client as mqtt

from .sensors.sensor import Sensor


def main():
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) != 2:
        raise ValueError("Must provide exactly one parameter")

    sensor_package_name = sys.argv[1]

    logger = logging.getLogger("main")
    client = mqtt.Client(client_id=f"sensord-reader-{sensor_package_name}", clean_session=True)

    logger.info("Starting MQTT Client")
    client.connect_async("127.0.0.1")
    client.loop_start()

    logger.info("Creating Sensor")

    SensorClass = import_module(".sensors." + sensor_package_name, __package__).SENSOR_CLASS

    sensor: Sensor = SensorClass(client)
    sensor.start()

    logger.error("sensor exited unexpectedly")
    sys.exit(1)


if __name__ == "__main__":
    main()
