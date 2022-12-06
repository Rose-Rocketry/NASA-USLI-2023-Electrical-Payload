from .sensor import PollingSensor
from lib_sensor_encoding import SensorMeta, EncodingType, TimestampReading
from .mpl3115_interface import MPL3115Interface

class MPL3115Sensor(PollingSensor):
    def _get_sensor_name(self) -> str:
        return "mpl3115"

    def _get_sensor_metadata(self) -> SensorMeta:
        return {
            "name":
            "MPL3115",
            "readings": [
                TimestampReading,
                {
                    "name": "altitude",
                    "unit": "m",
                    "encoding": EncodingType.bits_integer_scaled,
                    "bits": 24,
                    "lsb_value": 1 / 256,
                    "signed": False,
                },
                {
                    "name": "temperature",
                    "unit": "°C",
                    "encoding": EncodingType.bits_integer_scaled,
                    "bits": 16,
                    "lsb_value": 1 / 256,
                    "signed": True,
                },
            ],
        }

    def _get_sensor_poll_rate(self) -> float:
        return 5

    def _run(self) -> None:
        self._interface = MPL3115Interface()

        return super()._run()

    def _poll(self) -> None:
        data = self._interface.read_data()
        self._client.publish_sensor_data_raw(self._get_sensor_name(), data)

SENSOR_CLASS = MPL3115Sensor
