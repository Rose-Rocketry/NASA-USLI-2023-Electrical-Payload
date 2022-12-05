from .sensor import PollingSensor
from lib_sensor_encoding import SensorMeta, EncodingType, TimestampReading


class CPUTemperatureSensor(PollingSensor):

    def _get_sensor_name(self) -> str:
        return "cpu_temperature"

    def _get_sensor_metadata(self) -> SensorMeta:
        return {
            "name":
            "CPU Temperature",
            "readings": [
                TimestampReading,
                {
                    "name": "temperature",
                    "unit": "°C",
                    "encoding": EncodingType.bits_integer_scaled,
                    "bits": 16,
                    "lsb_value": 0.01,
                },
            ],
        }

    def _get_sensor_poll_rate(self) -> float:
        return 0.5

    def _poll(self) -> None:
        with open("/sys/class/thermal/thermal_zone0/temp", "rt") as file:
            temperature = int(file.read()) / 1000

        self._publish(temperature=temperature)
