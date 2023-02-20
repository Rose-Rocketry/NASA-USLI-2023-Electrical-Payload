from .sensor import PollingSensor
from .mpl3115_interface import MPL3115Interface


class MPL3115Sensor(PollingSensor):
    def _get_sensor_id(self) -> str:
        return "mpl3115"

    def _get_sensor_metadata(self):
        return {
            "name": "MPL3115",
            "channels": [
                {
                    "key": "altitude",
                    "name": "Altitude",
                    "type": "number",
                    "unit": "m",
                },
                {
                    "key": "temp",
                    "name": "Temperature",
                    "type": "number",
                    "unit": "\u00b0C",
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
        self.publish(data)


SENSOR_CLASS = MPL3115Sensor
