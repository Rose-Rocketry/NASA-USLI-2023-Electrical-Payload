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

            if data["class"] == "TPV":
                mode = data["mode"]
                print(data)
                if mode == 1 and "time" in data:
                    self.log_values(data["time"], data["mode"], data["ept"],
                                    "", "", "", "", "", "", raw)
                elif mode == 2:
                    self.log_values(data["time"], data["mode"], data["ept"],
                                    data["lat"], data["lon"], data["epx"],
                                    data["epy"], "", "", "", raw)
                elif mode == 3:
                    self.log_values(data["time"], data["mode"], data["ept"],
                                    data["lat"], data["lon"], data["epx"],
                                    data["epy"], data["alt"], data["epv"], raw)
                else:
                    self.log_values("", data["mode"], "", "", "", "", "", "", "", raw)
