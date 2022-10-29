from ast import While
import asyncio
from pathlib import Path
from re import S
import time
from .logger import Logger
from Adafruit_PureIO.smbus import SMBus

class MPULogger(Logger):
    bus = SMBus(3)

    def __init__(self, session_folder: Path) -> None:
        super().__init__(session_folder, "MPU6050", ("ax", "ay", "az", "rx", "ry", "rz"))

    async def start(self):
        self.bus = SMBus(3)
