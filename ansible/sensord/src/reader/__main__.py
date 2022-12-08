from lib_sensor_encoding import MQTTSensorClient
from threading import Thread
from time import sleep
from importlib import import_module
import logging
import sys

from .sensors.sensor import Sensor


def main():
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) != 2:
        raise ValueError("Must provide exactly one parameter")

    sensor_package_name = sys.argv[1]

    logger = logging.getLogger("main")
    client = MQTTSensorClient()

    logger.info("Starting MQTT Client")
    client.run_background()

    logger.info("Creating Sensor")

    SensorClass = import_module(".sensors." + sensor_package_name, __package__).SENSOR_CLASS

    sensor: Sensor = SensorClass(client)
    sensor.start()

    logger.error("sensor exited unexpectedly")
    sys.exit(1)


if __name__ == "__main__":
    main()
