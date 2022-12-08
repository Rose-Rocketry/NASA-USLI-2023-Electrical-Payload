from .sensor import PollingSensor
from lib_sensor_encoding import SensorMeta, EncodingType, TimestampReading
from .mpu6050_interface import MPU6050Interface, AccelRange, GyroRange, Bandwidth, Rate


class MPU6050Sensor(PollingSensor):
    _interface: MPU6050Interface
    _ACCEL = AccelRange.RANGE_2_G
    _GYRO = GyroRange.RANGE_250_DPS
    _BANDWIDTH = Bandwidth.BAND_5_HZ # Apply a ~5Hz lowpass filter within the sensor
    _RATE = Rate.CYCLE_5_HZ # Generate new data at a rate of 5Hz (also used as the update rate)

    def _get_sensor_name(self) -> str:
        return "mpu6050"

    def _get_sensor_metadata(self) -> SensorMeta:
        MPU6050AccelAxis = {
            "unit": "g",
            "encoding": EncodingType.bits_integer_scaled,
            "signed": True,
            "bits": 16,
            "lsb_value": self._ACCEL.lsb,
        }

        MPU6050GyroAxis = {
            "unit": "°/s",
            "encoding": EncodingType.bits_integer_scaled,
            "signed": True,
            "bits": 16,
            "lsb_value": self._GYRO.lsb,
        }

        return {
            "name":
            "MPU6050",
            "readings": [
                TimestampReading,
                { "name": "ax" } | MPU6050AccelAxis,
                { "name": "ay" } | MPU6050AccelAxis,
                { "name": "az" } | MPU6050AccelAxis,
                {
                    "name": "temperature",
                    "unit": "°C",
                    "encoding": EncodingType.bits_integer_scaled,
                    "bits": 16,
                    "lsb_value": 1 / 340,
                    "zero_value": 36.53
                },
                { "name": "gx" } | MPU6050GyroAxis,
                { "name": "gy" } | MPU6050GyroAxis,
                { "name": "gz" } | MPU6050GyroAxis,
            ],
        }

    def _get_sensor_poll_rate(self) -> float:
        return self._RATE.rate

    def _run(self) -> None:
        self._interface = MPU6050Interface(self._ACCEL, self._GYRO,
                                           self._BANDWIDTH, self._RATE)

        return super()._run()

    def _poll(self) -> None:
        data = self._interface.read_data()
        self._client.publish_sensor_data_raw(self._get_sensor_name(), data)

SENSOR_CLASS = MPU6050Sensor
