from .sensor import PollingSensor
from pathlib import Path
import psutil
import paho.mqtt.client as mqtt

class SystemSensor(PollingSensor):
    def __init__(self, client: mqtt.Client) -> None:
        super().__init__(client)

    def _get_sensor_id(self) -> str:
        return "system"

    def _get_sensor_metadata(self):
        return {
            "name": "System Status",
            "channels": [
                {"name": "timestamp", "type": "timestamp"},
                {
                    "name": "CPU Temperature",
                    "type": "number",
                    "unit": "°C",
                    "scale": 10,
                },
                {
                    "name": "CPU Usage",
                    "type": "number",
                    "unit": "%",
                    "scale": 100,
                    "minimum": 0,
                    "maximum": 100,
                },
                {
                    "name": "CPU Frequency",
                    "type": "number",
                    "unit": "MHz",
                    "scale": 1,
                },
                {
                    "name": "Memory Usage",
                    "type": "number",
                    "unit": "%",
                    "scale": 10,
                    "minimum": 0,
                    "maximum": 100,
                },
                {
                    "name": "Swap Usage",
                    "type": "number",
                    "unit": "%",
                    "scale": 10,
                    "minimum": 0,
                    "maximum": 100,
                },
                {
                    "name": "Disk Usage",
                    "type": "number",
                    "unit": "%",
                    "scale": 10,
                    "minimum": 0,
                    "maximum": 100,
                },
            ],
        }

    def _get_sensor_poll_rate(self) -> float:
        return 0.5

    def _poll(self) -> None:
        cpu_usage = psutil.cpu_percent()
        cpu_frequency = psutil.cpu_freq().current
        memory_usage = psutil.virtual_memory().percent
        swap_usage = psutil.swap_memory().percent
        disk_usage = psutil.disk_usage("/").percent

        cpu_temperature = None
        temperature_data = psutil.sensors_temperatures()
        if "cpu_thermal" in temperature_data:
            cpu_temperature = temperature_data['cpu_thermal'][0].current

        self.publish(
            {
                "cpu_temperature": cpu_temperature,
                "cpu_usage": cpu_usage,
                "cpu_frequency": cpu_frequency,
                "memory_usage": memory_usage,
                "swap_usage": swap_usage,
                "disk_usage": disk_usage,
            },
        )


SENSOR_CLASS = SystemSensor
