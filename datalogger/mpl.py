import asyncio
from pathlib import Path
from Adafruit_PureIO.smbus import SMBus

from .logger import Logger

# Based on code from https://github.com/adafruit/Adafruit_CircuitPython_MPL3115A2/blob/main/adafruit_mpl3115a2.py

_MPL3115A2_ADDRESS = 0x60
_MPL3115A2_REGISTER_STATUS = 0x00
_MPL3115A2_REGISTER_PRESSURE_MSB = 0x01
_MPL3115A2_REGISTER_PRESSURE_CSB = 0x02
_MPL3115A2_REGISTER_PRESSURE_LSB = 0x03
_MPL3115A2_REGISTER_TEMP_MSB = 0x04
_MPL3115A2_REGISTER_TEMP_LSB = 0x05
_MPL3115A2_REGISTER_DR_STATUS = 0x06
_MPL3115A2_OUT_P_DELTA_MSB = 0x07
_MPL3115A2_OUT_P_DELTA_CSB = 0x08
_MPL3115A2_OUT_P_DELTA_LSB = 0x09
_MPL3115A2_OUT_T_DELTA_MSB = 0x0A
_MPL3115A2_OUT_T_DELTA_LSB = 0x0B
_MPL3115A2_WHOAMI = 0x0C
_MPL3115A2_BAR_IN_MSB = 0x14
_MPL3115A2_BAR_IN_LSB = 0x15

_MPL3115A2_REGISTER_STATUS_TDR = 0x02
_MPL3115A2_REGISTER_STATUS_PDR = 0x04
_MPL3115A2_REGISTER_STATUS_PTDR = 0x08

_MPL3115A2_PT_DATA_CFG = 0x13
_MPL3115A2_PT_DATA_CFG_TDEFE = 0x01
_MPL3115A2_PT_DATA_CFG_PDEFE = 0x02
_MPL3115A2_PT_DATA_CFG_DREM = 0x04

_MPL3115A2_CTRL_REG1 = 0x26
_MPL3115A2_CTRL_REG2 = 0x27
_MPL3115A2_CTRL_REG3 = 0x28
_MPL3115A2_CTRL_REG4 = 0x29
_MPL3115A2_CTRL_REG5 = 0x2A

_MPL3115A2_CTRL_REG1_SBYB = 0x01
_MPL3115A2_CTRL_REG1_OST = 0x02
_MPL3115A2_CTRL_REG1_RST = 0x04
_MPL3115A2_CTRL_REG1_RAW = 0x40
_MPL3115A2_CTRL_REG1_ALT = 0x80
_MPL3115A2_CTRL_REG1_BAR = 0x00

_MPL3115A2_CTRL_REG1_OS1 = 0x00
_MPL3115A2_CTRL_REG1_OS2 = 0x08
_MPL3115A2_CTRL_REG1_OS4 = 0x10
_MPL3115A2_CTRL_REG1_OS8 = 0x18
_MPL3115A2_CTRL_REG1_OS16 = 0x20
_MPL3115A2_CTRL_REG1_OS32 = 0x28
_MPL3115A2_CTRL_REG1_OS64 = 0x30
_MPL3115A2_CTRL_REG1_OS128 = 0x38

_MPL3115A2_REGISTER_STARTCONVERSION = 0x12


class MPLLogger(Logger):

    def __init__(self, session_folder: Path, bus: SMBus) -> None:
        super().__init__(session_folder, "MPL3115", ("temp", "altitude"))

        self.bus = bus

    async def start(self):
        # Over sample, measure altitude
        self.ctrl_reg1 = _MPL3115A2_CTRL_REG1_OS64 | _MPL3115A2_CTRL_REG1_ALT

        # Reset chip
        try:
            self.bus.write_byte_data(_MPL3115A2_ADDRESS, _MPL3115A2_CTRL_REG1,
                                     _MPL3115A2_CTRL_REG1_RST)
        except IOError:
            pass  # This is expected

        # Wait for reset
        await asyncio.sleep(0.01)
        while self.bus.read_byte_data(
                _MPL3115A2_ADDRESS,
                _MPL3115A2_CTRL_REG1) & _MPL3115A2_CTRL_REG1_RST > 0:
            await asyncio.sleep(0.01)

        # Set config
        self.bus.write_byte_data(_MPL3115A2_ADDRESS, _MPL3115A2_CTRL_REG1,
                                 self.ctrl_reg1)
        self.bus.write_byte_data(
            _MPL3115A2_ADDRESS, _MPL3115A2_PT_DATA_CFG,
            _MPL3115A2_PT_DATA_CFG_DREM | _MPL3115A2_PT_DATA_CFG_PDEFE
            | _MPL3115A2_PT_DATA_CFG_TDEFE)

        self.ctrl_reg1 |= _MPL3115A2_CTRL_REG1_OST
        while True:
            self.bus.write_byte_data(_MPL3115A2_ADDRESS, _MPL3115A2_CTRL_REG1,
                                     self.ctrl_reg1)

            mpl3115_bytes = self.bus.read_i2c_block_data(
                _MPL3115A2_ADDRESS, 0x00, 6)

            status_byte = mpl3115_bytes[0]
            if status_byte == 0:
                await asyncio.sleep(0.01)
                continue

            altitude_bytes = mpl3115_bytes[1:4]
            temperature_bytes = mpl3115_bytes[4:]

            altitude = int.from_bytes(
                altitude_bytes,
                "big",
                signed=False,
            ) / 256
            temperature = int.from_bytes(
                temperature_bytes,
                "big",
                signed=True,
            ) / 256

            self.log_values(temperature, altitude)
