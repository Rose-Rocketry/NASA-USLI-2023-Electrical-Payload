from .sensor import PollingSensor
from .bno055_interface import BNO055Interface


class BNO055Sensor(PollingSensor):
    _interface: BNO055Interface

    def _get_sensor_id(self) -> str:
        return "bno055"

    def _get_sensor_metadata(self):
        return {
            "name": "BNO055 - IMU Mode",
            "channels": [
                {
                    "key": "gravity",
                    "name": "Gravity",
                    "type": "vector",
                    "unit": "m/s\u00b2",
                    "components": ["x", "y", "z"],
                    "minimum": -20,
                    "maximum": 20,
                },
            ],
        }

    def _get_sensor_poll_rate(self) -> float:
        return 10

    def _run(self) -> None:
        self._interface = BNO055Interface()

        return super()._run()

    def _poll(self) -> None:
        data = self._interface.read_data()
        self.publish(data)


SENSOR_CLASS = BNO055Sensor
