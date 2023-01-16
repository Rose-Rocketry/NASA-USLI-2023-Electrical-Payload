from .sensor import PollingSensor
from lib_sensor_encoding import SensorMeta, EncodingType, TimestampReading

class MCP3004Sensor(PollingSensor):
    LSB_VALUE = 1/27.6982857142857

    def _get_sensor_name(self) -> str:
        return "battery"

    def _get_sensor_metadata(self) -> SensorMeta:
        return {
            "name":
            "MPL3115",
            "readings": [
                TimestampReading,
                {
                    "name": "voltage",
                    "unit": "V",
                    "encoding": EncodingType.bits_integer_scaled,
                    "bits": 16,
                    "lsb_value": self.LSB_VALUE,
                    "signed": False,
                },
            ],
        }

    def _get_sensor_poll_rate(self) -> float:
        return 2

    def _run(self) -> None:
        self._fd = open("/sys/bus/iio/devices/iio:device0/in_voltage0_raw", "rb", buffering=0)

        return super()._run()

    def _poll(self) -> None:
        self._fd.seek(0)
        data = int(self._fd.read())

        self._client.publish_sensor_data_raw(self._get_sensor_name(), data.to_bytes(2, 'big'))

SENSOR_CLASS = MCP3004Sensor
