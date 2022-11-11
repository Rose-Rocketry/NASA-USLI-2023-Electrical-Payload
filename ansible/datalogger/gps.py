import asyncio
from base64 import b64encode
import json
from pathlib import Path

from .logger import Logger


class GPSDLogger(Logger):

    def __init__(self, session_folder: Path) -> None:
        super().__init__(
            session_folder,
            "GPSD",
            ("time", "fix", "ept", "lat", "lon", "epx", "epy", "alt", "epv"),
        )

    async def start(self):
        reader, writer = await asyncio.open_connection("localhost", 2947)

        writer.write(b'?WATCH={"enable":true,"json":true}\n')

        async for line in reader:
            data = json.loads(line)
            raw = b64encode(line).decode()

            if data.get("class") == "TPV":
                self.log_values(data.get("time"), data.get("mode"), data.get("ept"),
                                data.get("lat"), data.get("lon"), data.get("epx"),
                                data.get("epy"), data.get("alt"), data.get("epv"), raw)
