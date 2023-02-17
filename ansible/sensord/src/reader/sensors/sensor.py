from threading import Thread
from typing import Callable
from abc import ABC, abstractmethod
import logging
import time
import paho.mqtt.client as mqtt
import json

META_TRANSMIT_INTERVAL = 15
SENSOR_PREFIX = "sensors/"

class Sensor(ABC):
    def __init__(self, client: mqtt.Client) -> None:
        self._client = client
        self._logger = logging.getLogger(f"sensor.{self._get_sensor_id()}")

    @abstractmethod
    def _get_sensor_metadata(self):
        pass

    @abstractmethod
    def _get_sensor_id(self) -> str:
        pass

    @abstractmethod
    def _run(self) -> None:
        pass

    def _send_meta_thread(self):
        pass
        # meta = msgpack.packb(self._get_sensor_metadata)
        # while True:
        #     self._client

    def publish(self, data, **kwargs):
        if "timestamp" not in data:
            data["timestamp"] = time.time()

        self._client.publish(SENSOR_PREFIX + self._get_sensor_id(), json.dumps(data), **kwargs)

    def start(self) -> Thread:
        self._run()


POLL_BACKOFF = 1
POLL_BACKOFF_COUNT = 5

class PollingSensor(Sensor):
    def __init__(self, client: mqtt.Client) -> None:
        self._failed_polls = 0

        super().__init__(client)

    def _run(self) -> None:
        delay = 1 / self._get_sensor_poll_rate()
        next_reading = 0
        while True:
            
            now = time.monotonic()
            next_reading += delay
            if (now > next_reading):
                next_reading = now  # Sensor read took too long
            else:
                time.sleep(next_reading - now)

            try:
                self._poll()
                self._failed_polls = 0
            except Exception as e:
                self._logger.error("Error reading sensor:")
                self._logger.error(e, exc_info=True)
                self._failed_polls += 1
                if self._failed_polls >= POLL_BACKOFF_COUNT:
                    self._logger.error("To many errors, exiting")
                    return

                time.sleep(POLL_BACKOFF)

    @abstractmethod
    def _get_sensor_poll_rate(self) -> float:
        pass

    @abstractmethod
    def _poll(self) -> None:
        pass
