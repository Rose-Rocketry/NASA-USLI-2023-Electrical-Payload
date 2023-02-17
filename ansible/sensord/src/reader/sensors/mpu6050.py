from .sensor import PollingSensor
# from .mpu6050_interface import MPU6050Interface, AccelRange, GyroRange, Bandwidth, Rate
from .mpu6050_interface_iio import MPU6050Interface


class MPU6050Sensor(PollingSensor):
    _interface: MPU6050Interface
    # _ACCEL = AccelRange.RANGE_2_G
    # _GYRO = GyroRange.RANGE_250_DPS
    # _BANDWIDTH = Bandwidth.BAND_5_HZ # Apply a ~5Hz lowpass filter within the sensor
    # _RATE = Rate.CYCLE_40_HZ # Generate new data at a rate of 5Hz (also used as the update rate)

    def _get_sensor_id(self) -> str:
        return "mpu6050"

    def _get_sensor_metadata(self):
        return {}

        # MPU6050AccelAxis = {
        #     "unit": "g",
        #     "encoding": EncodingType.bits_integer_scaled,
        #     "signed": True,
        #     "bits": 16,
        #     "lsb_value": self._ACCEL.lsb,
        # }

        # MPU6050GyroAxis = {
        #     "unit": "°/s",
        #     "encoding": EncodingType.bits_integer_scaled,
        #     "signed": True,
        #     "bits": 16,
        #     "lsb_value": self._GYRO.lsb,
        # }

        # return {
        #     "name":
        #     "MPU6050",
        #     "readings": [
        #         TimestampReading,
        #         { "name": "ax" } | MPU6050AccelAxis,
        #         { "name": "ay" } | MPU6050AccelAxis,
        #         { "name": "az" } | MPU6050AccelAxis,
        #         {
        #             "name": "temperature",
        #             "unit": "°C",
        #             "encoding": EncodingType.bits_integer_scaled,
        #             "bits": 16,
        #             "lsb_value": 1 / 340,
        #             "zero_value": 36.53
        #         },
        #         { "name": "gx" } | MPU6050GyroAxis,
        #         { "name": "gy" } | MPU6050GyroAxis,
        #         { "name": "gz" } | MPU6050GyroAxis,
        #     ],
        # }

    def _get_sensor_poll_rate(self) -> float:
        # return self._RATE.rate
        return 5

    def _run(self) -> None:
        # self._interface = MPU6050Interface(self._ACCEL, self._GYRO,
        #                                    self._BANDWIDTH, self._RATE)
        self._interface = MPU6050Interface()

        return super()._run()

    def _poll(self) -> None:
        data = self._interface.read_data()
        self.publish(data)

SENSOR_CLASS = MPU6050Sensor
