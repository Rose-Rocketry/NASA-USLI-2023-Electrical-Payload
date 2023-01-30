from .sensor import Sensor
from lib_sensor_encoding import SensorMeta, EncodingType, TimestampReading
from datetime import datetime
import asyncio
import json


class GPSDSensor(Sensor):

    def _get_sensor_id(self) -> str:
        return "gpsd"

    def _get_sensor_metadata(self) -> SensorMeta:
        return {
            "name": "gpsd",
            "readings": [
                TimestampReading,
                {
                    "name": "fix_mode",
                    "unit": "",
                    "encoding": EncodingType.bits_integer_scaled,
                    "bits": 8,
                    "signed": True,
                },
                {
                    "name": "gps_timestamp",
                    "encoding": EncodingType.timestamp,
                    "bits": 64,
                },
                {
                    "name": "latitude",
                    "unit": "°",
                    "encoding": EncodingType.bits_integer_scaled,
                    "bits": 32,
                    "lsb_value": 180 / 2**32,
                    "signed": True,
                },
                {
                    "name": "longitude",
                    "unit": "°",
                    "encoding": EncodingType.bits_integer_scaled,
                    "bits": 32,
                    "lsb_value": 360 / 2**32,
                    "signed": True,
                },
                {
                    "name": "altitude",
                    "unit": "m",
                    "encoding": EncodingType.float,
                    "bits": 32,
                },
            ],
        }

    def _get_sensor_poll_rate(self) -> float:
        return 100  # Just rate limits reading, actual speed is ~1Hz

    def _run(self) -> None:
        asyncio.get_event_loop().run_until_complete(self._async_run())

        raise RuntimeError("async loop exited unexpectedly")

    async def _async_run(self):
        reader, writer = await asyncio.open_connection("localhost", 2947)

        writer.write(b'?WATCH={"enable":true,"json":true}\n')

        async for line in reader:
            data = json.loads(line)

            mode = data.get("mode", -1)
            time = data.get("time", "1970-01-01T00:00:00.000Z")
            time = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%f%z")
            lat = data.get("lat", 0)
            lon = data.get("lon", 0)
            alt = data.get("alt", 0)

            print(f"Time: {time}")

            self._publish(fix_mode=mode,
                          gps_timestamp=time,
                          latitude=lat,
                          longitude=lon,
                          altitude=alt)


SENSOR_CLASS = GPSDSensor
