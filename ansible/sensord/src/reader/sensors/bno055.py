from .sensor import PollingSensor
from .bno055_interface import BNO055Interface


class BNO055Sensor(PollingSensor):
    _interface: BNO055Interface

    def _get_sensor_id(self) -> str:
        return "bno055"

    def _get_sensor_metadata(self):
        return {}

    def _get_sensor_poll_rate(self) -> float:
        return 5

    def _run(self) -> None:
        self._interface = BNO055Interface()

        return super()._run()

    def _poll(self) -> None:
        data = self._interface.read_data()
        self.publish(data)

SENSOR_CLASS = BNO055Sensor
