from enum import Enum
from time import sleep
from Adafruit_PureIO.smbus import SMBus
# from smbus import SMBus

# Based on code from https://github.com/adafruit/Adafruit_CircuitPython_MPU6050/blob/main/adafruit_mpu6050.py

_BNO055_ADDR = 0x28
_BNO055_CHIP_ID = 0x00
_BNO055_CHIP_VALUE = 0xA0
_BNO055_OPR_MODE = 0x3D
_BNO055_OPR_MODE_ACCONLY = 0x01
_BNO055_OPR_MODE_IMU = 0x08
_BNO055_ACC_DATA_START = 0x08
_BNO055_GRV_DATA_START = 0x2E


class BNO055Interface:

    def __init__(self) -> None:
        self.bus = SMBus(4)

        if self.bus.read_byte_data(_BNO055_ADDR, _BNO055_CHIP_ID) != _BNO055_CHIP_VALUE:
            raise Exception("Invalid CHIP_ID value")

        self.bus.write_byte_data(
            _BNO055_ADDR,
            _BNO055_OPR_MODE,
            _BNO055_OPR_MODE_IMU,
        )

    def read_data(self) -> bytes:
        data = self.bus.read_i2c_block_data(
            _BNO055_ADDR,
            _BNO055_GRV_DATA_START,
            6,
        )

        ax = int.from_bytes(data[0:2], 'little', signed=True) * 0.01
        ay = int.from_bytes(data[2:4], 'little', signed=True) * 0.01
        az = int.from_bytes(data[4:6], 'little', signed=True) * 0.01

        return {
            "gravity": (ax, ay, az),
        }
