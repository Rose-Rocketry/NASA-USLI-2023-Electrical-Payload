from .sensor import PollingSensor
from pathlib import Path
import psutil
import paho.mqtt.client as mqtt
from humanize import naturalsize


class SystemSensor(PollingSensor):
    def __init__(self, client: mqtt.Client) -> None:
        super().__init__(client)

    def _get_sensor_id(self) -> str:
        return "system"

    def _get_sensor_metadata(self):
        return {
            "name": "System Status",
            "channels": [
                {
                    "key": "cpu_temp",
                    "name": "CPU Temperature",
                    "type": "number",
                    "unit": "°C",
                },
                {
                    "key": "cpu_usage",
                    "name": f"CPU Usage ({psutil.cpu_count()} cores)",
                    "type": "number",
                    "unit": "%",
                    "minimum": 0,
                    "maximum": 100,
                },
                {
                    "key": "cpu_freq",
                    "name": "CPU Frequency",
                    "type": "number",
                    "unit": "MHz",
                    "minimum": 0,
                    "maximum": 1000,
                },
                {
                    "key": "mem_usage",
                    "name": "Memory Usage",
                    "type": "vector",
                    "components": (
                        f"memory ({naturalsize(psutil.virtual_memory().total, True)})",
                        f"swap ({naturalsize(psutil.swap_memory().total, True)})",
                    ),
                    "unit": "%",
                    "minimum": 0,
                    "maximum": 100,
                },
                {
                    "key": "disk_usage",
                    "name": "Disk Usage",
                    "type": "number",
                    "unit": "%",
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
            cpu_temperature = temperature_data["cpu_thermal"][0].current

        self.publish(
            {
                "cpu_temp": cpu_temperature,
                "cpu_usage": cpu_usage,
                "cpu_freq": cpu_frequency,
                "mem_usage": (memory_usage, swap_usage),
                "swap_usage": swap_usage,
                "disk_usage": disk_usage,
            },
        )


SENSOR_CLASS = SystemSensor
