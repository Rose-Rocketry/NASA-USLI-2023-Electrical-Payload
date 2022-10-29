from pathlib import Path
from Adafruit_PureIO.smbus import SMBus

from .logger import Logger


class MPULogger(Logger):
    bus = SMBus(3)

    def __init__(self, session_folder: Path) -> None:
        super().__init__(session_folder, "MPU6050",
                         ("ax", "ay", "az", "rx", "ry", "rz"))

    async def start(self):
        self.bus = SMBus(3)
