import asyncio
from enum import Enum
from pathlib import Path
from struct import Struct
from Adafruit_PureIO.smbus import SMBus

from .logger import Logger

# Based on code from https://github.com/adafruit/Adafruit_CircuitPython_MPU6050/blob/main/adafruit_mpu6050.py

_MPU6050_DEFAULT_ADDRESS = 0x68  # MPU6050 default i2c address w/ AD0 low
_MPU6050_DEVICE_ID = 0x68  # The correct MPU6050_WHO_AM_I value

_MPU6050_SELF_TEST_X = 0x0D  # Self test factory calibrated values register
_MPU6050_SELF_TEST_Y = 0x0E  # Self test factory calibrated values register
_MPU6050_SELF_TEST_Z = 0x0F  # Self test factory calibrated values register
_MPU6050_SELF_TEST_A = 0x10  # Self test factory calibrated values register
_MPU6050_SMPLRT_DIV = 0x19  # sample rate divisor register
_MPU6050_CONFIG = 0x1A  # General configuration register
_MPU6050_GYRO_CONFIG = 0x1B  # Gyro specfic configuration register
_MPU6050_ACCEL_CONFIG = 0x1C  # Accelerometer specific configration register
_MPU6050_INT_PIN_CONFIG = 0x37  # Interrupt pin configuration register
_MPU6050_ACCEL_OUT = 0x3B  # base address for sensor data reads
_MPU6050_TEMP_OUT = 0x41  # Temperature data high byte register
_MPU6050_GYRO_OUT = 0x43  # base address for sensor data reads
_MPU6050_SIG_PATH_RESET = 0x68  # register to reset sensor signal paths
_MPU6050_USER_CTRL = 0x6A  # FIFO and I2C Master control register
_MPU6050_PWR_MGMT_1 = 0x6B  # Primary power/sleep control register
_MPU6050_PWR_MGMT_2 = 0x6C  # Secondary power/sleep control register
_MPU6050_WHO_AM_I = 0x75  # Divice ID register


class AccelRange(Enum):
    RANGE_2_G = (0, 1 / 16384)  # +/- 2g (default value)
    RANGE_4_G = (1, 1 / 8192)  # +/- 4g
    RANGE_8_G = (2, 1 / 4096)  # +/- 8g
    RANGE_16_G = (3, 1 / 2048)  # +/- 16g

    def __init__(self, i2c_value, lsb) -> None:
        self.i2c_value = i2c_value
        self.lsb = lsb


class GyroRange(Enum):
    RANGE_250_DPS = (0, 1 / 131)  # +/- 250 deg/s (default value)
    RANGE_500_DPS = (1, 2 / 131)  # +/- 500 deg/s
    RANGE_1000_DPS = (2, 4 / 131)  # +/- 1000 deg/s
    RANGE_2000_DPS = (3, 8 / 131)  # +/- 2000 deg/s

    def __init__(self, i2c_value, lsb) -> None:
        self.i2c_value = i2c_value
        self.lsb = lsb


class Bandwidth(Enum):
    BAND_260_HZ_NONE = 0  # Docs imply this disables the filter
    BAND_184_HZ = 1  # 184 Hz
    BAND_94_HZ = 2  # 94 Hz
    BAND_44_HZ = 3  # 44 Hz
    BAND_21_HZ = 4  # 21 Hz
    BAND_10_HZ = 5  # 10 Hz
    BAND_5_HZ = 6  # 5 Hz


class Rate(Enum):
    CYCLE_1_25_HZ = (0, 1.25)  # 1.25 Hz
    CYCLE_5_HZ = (1, 5)  # 5 Hz
    CYCLE_20_HZ = (2, 20)  # 20 Hz
    CYCLE_40_HZ = (4, 40)  # 40 Hz

    def __init__(self, i2c_value, rate) -> None:
        self.i2c_value = i2c_value
        self.rate = rate


class MPULogger(Logger):
    # Acceleration in G's, temperature

    data_struct = Struct(">hhhhhhh")

    def __init__(
        self,
        session_folder: Path,
        bus: SMBus,
        accel_range=AccelRange.RANGE_2_G,
        gyro_range=GyroRange.RANGE_250_DPS,
        bandwidth=Bandwidth.BAND_260_HZ_NONE,
        rate=Rate.CYCLE_5_HZ,
    ) -> None:
        super().__init__(
            session_folder,
            "MPU6050",
            ("Temperature (deg C)", "X Accel (G)", "Y Accel (G)", "Z Accel(G)",
             "X Gyro (deg/s)", "Y Gyro (deg/s)", "Z Gyro (deg/s)"),
        )

        self.bus = bus
        self.accel_range = accel_range
        self.gyro_range = gyro_range
        self.bandwidth = bandwidth
        self.rate = rate

    async def start(self):
        if self.bus.read_byte_data(_MPU6050_DEFAULT_ADDRESS,
                                   _MPU6050_WHO_AM_I) != _MPU6050_DEVICE_ID:
            raise Exception("Invalid WHO_AM_I value")

        self.bus.write_byte_data(
            _MPU6050_DEFAULT_ADDRESS,
            _MPU6050_CONFIG,
            self.bandwidth.value,
        )
        self.bus.write_byte_data(
            _MPU6050_DEFAULT_ADDRESS,
            _MPU6050_ACCEL_CONFIG,
            self.accel_range.i2c_value << 3,
        )
        self.bus.write_byte_data(
            _MPU6050_DEFAULT_ADDRESS,
            _MPU6050_GYRO_CONFIG,
            self.gyro_range.i2c_value << 3,
        )
        self.bus.write_byte_data(
            _MPU6050_DEFAULT_ADDRESS,
            _MPU6050_PWR_MGMT_1,
            0x00,
        )

        while True:
            # Approximate, doesn't account for runtime
            # await asyncio.sleep(1 / self.rate.rate)
            await asyncio.sleep(0.05)

            raw_data = self.bus.read_i2c_block_data(_MPU6050_DEFAULT_ADDRESS,
                                                    _MPU6050_ACCEL_OUT, 14)

            rax, ray, raz, rt, rgx, rgy, rgz = self.data_struct.unpack(
                raw_data)

            t = (rt / 340) + 36.53

            ax = rax * self.accel_range.lsb
            ay = ray * self.accel_range.lsb
            az = raz * self.accel_range.lsb

            gx = rgx * self.gyro_range.lsb
            gy = rgy * self.gyro_range.lsb
            gz = rgz * self.gyro_range.lsb

            self.log_values(t, ax, ay, az, gx, gy, gz)
