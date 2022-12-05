from lib_sensor_encoding import MQTTSensorClient, SensorMeta
from threading import Thread
from typing import Callable
from abc import ABC, abstractmethod
import time
import logging


class Sensor(ABC):
    _client: MQTTSensorClient
    _thread: Thread
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

    def __run(self) -> None:
        try:
            self._run()
        except Exception as e:
            self._logger.error("Error reading sensor:")
            self._logger.error(e, exc_info=True)

    def start(self) -> Thread:
        self._publish = self._client.create_sensor(self._get_sensor_name(),
                                                   self._get_sensor_metadata())

        self._thread = Thread(
            name=f"Sensor {self._get_sensor_name()}",
            target=self.__run,
            daemon=True,
        )
        self._thread.start()

        return self._thread


POLL_BACKOFF = 5


class PollingSensor(Sensor):

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
            except Exception as e:
                self._logger.error("Error reading sensor:")
                self._logger.error(e, exc_info=True)
                time.sleep(POLL_BACKOFF)

    @abstractmethod
    def _get_sensor_poll_rate(self) -> float:
        pass

    @abstractmethod
    def _poll(self) -> None:
        pass
