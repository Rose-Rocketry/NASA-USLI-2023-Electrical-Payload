import asyncio
import json
from pathlib import Path
from .logger import Logger


class GPSDLogger(Logger):

    def __init__(self, session_folder: Path) -> None:
        super().__init__(
            session_folder, "GPSD",
            ("time", "fix", "ept", "lat", "lon", "epx", "epy", "alt", "epv"))

    async def start(self):
        reader, writer = await asyncio.open_connection("localhost", 2947)

        writer.write(b'?WATCH={"enable":true,"json":true}\n')

        async for line in reader:
            data = json.loads(line)

            if data['class'] == 'TPV':
                mode = data["mode"]
                if mode == 1:
                    self.log_values(data["time"], data["mode"], data["ept"])
                elif mode == 2:
                    self.log_values(data["time"], data["mode"], data["ept"],
                                    data["lat"], data["lon"], data["epx"],
                                    data["epy"])
                elif mode == 3:
                    self.log_values(data["time"], data["mode"], data["ept"],
                                    data["lat"], data["lon"], data["epx"],
                                    data["epy"], data["alt"], data["epv"])
