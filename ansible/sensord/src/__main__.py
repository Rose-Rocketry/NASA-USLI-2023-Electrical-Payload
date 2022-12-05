from lib_sensor_encoding import MQTTSensorClient
from threading import Thread
from time import sleep
import logging
import sys

from .sensors.sensor import Sensor
from .sensors.cpu_temperature import CPUTemperatureSensor
from .sensors.mpu6050 import MPU6050Sensor
from .sensors.mpl3115 import MPL3115Sensor


def main():
    logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger("main")
    client = MQTTSensorClient()

    logger.info("Starting MQTT Client")
    client_thread = Thread(name="MQTT Client",
                           target=client.run_foreground,
                           daemon=True)
    client_thread.start()

    logger.info("Creating Sensors")
    sensors: list[Sensor] = [
        CPUTemperatureSensor(client),
        MPU6050Sensor(client),
        MPL3115Sensor(client),
    ]

    threads = [
        *map(lambda sensor: sensor.start(), sensors),
        client_thread,
    ]

    logger.info("Monitoring Threads")

    while True:
        for thread in threads:
            if not thread.is_alive():
                logger.error(f"Thread {repr(thread.name)} exited unexpectedly")
                sys.exit(1)

        sleep(5)


if __name__ == "__main__":
    main()
