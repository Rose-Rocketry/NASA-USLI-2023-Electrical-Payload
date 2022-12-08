from .sensor import PollingSensor
from lib_sensor_encoding import SensorMeta, EncodingType, TimestampReading
from pathlib import Path
import psutil


CPU_TEMP_PATH = Path("/sys/class/thermal/thermal_zone0/temp")

class SystemSensor(PollingSensor):

    def _get_sensor_name(self) -> str:
        return "system"

    def _get_sensor_metadata(self) -> SensorMeta:
        return {
            "name":
            "System Status",
            "readings": [
                TimestampReading,
                {
                    "name": "cpu_temperature",
                    "unit": "°C",
                    "encoding": EncodingType.bits_integer_scaled,
                    "bits": 16,
                    "lsb_value": 0.01,
                },
                {
                    "name": "cpu_usage",
                    "unit": "%",
                    "encoding": EncodingType.bits_integer_scaled,
                    "bits": 16,
                    "lsb_value": 0.01,
                },
                {
                    "name": "cpu_frequency",
                    "unit": "MHz",
                    "encoding": EncodingType.bits_integer_scaled,
                    "bits": 16,
                    "lsb_value": 0.1,
                },
                {
                    "name": "memory_usage",
                    "unit": "%",
                    "encoding": EncodingType.bits_integer_scaled,
                    "bits": 16,
                    "lsb_value": 0.1,
                },
                {
                    "name": "swap_usage",
                    "unit": "%",
                    "encoding": EncodingType.bits_integer_scaled,
                    "bits": 16,
                    "lsb_value": 0.1,
                },
                {
                    "name": "disk_usage",
                    "unit": "%",
                    "encoding": EncodingType.bits_integer_scaled,
                    "bits": 16,
                    "lsb_value": 0.1,
                },
            ],
        }

    def _get_sensor_poll_rate(self) -> float:
        return 0.5

    def _poll(self) -> None:
        cpu_temperature = 0

        if CPU_TEMP_PATH.exists():
            with open(CPU_TEMP_PATH, "rt") as file:
                cpu_temperature = int(file.read()) / 1000

        cpu_usage = psutil.cpu_percent()
        cpu_frequency = psutil.cpu_freq().current
        memory_usage = psutil.virtual_memory().percent
        swap_usage = psutil.swap_memory().percent
        disk_usage = psutil.disk_usage("/").percent

        self._publish(
            cpu_temperature=cpu_temperature,
            cpu_usage=cpu_usage,
            cpu_frequency=cpu_frequency,
            memory_usage=memory_usage,
            swap_usage=swap_usage,
            disk_usage=disk_usage,
        )


SENSOR_CLASS = SystemSensor
