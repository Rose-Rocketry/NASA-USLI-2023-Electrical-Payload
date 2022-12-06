from lib_sensor_encoding import MQTTSensorClient, SensorMeta
from threading import Thread
from typing import Callable
from abc import ABC, abstractmethod
import time
import logging


class Sensor(ABC):
    _client: MQTTSensorClient
    _publish: Callable

    def __init__(self, client: MQTTSensorClient) -> None:
        self._client = client
        self._logger = logging.getLogger(f"sensor.{self._get_sensor_name()}")

    @abstractmethod
    def _get_sensor_metadata(self) -> SensorMeta:
        pass

    @abstractmethod
    def _get_sensor_name(self) -> str:
        pass

    @abstractmethod
    def _run(self) -> None:
        pass

    def start(self) -> Thread:
        self._publish = self._client.create_sensor(self._get_sensor_name(),
                                                   self._get_sensor_metadata())

        self._run()


POLL_BACKOFF = 1
POLL_BACKOFF_COUNT = 5

class PollingSensor(Sensor):
    def __init__(self, client: MQTTSensorClient) -> None:
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
