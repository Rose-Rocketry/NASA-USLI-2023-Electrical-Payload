import asyncio
import time
from subprocess import call
from shutil import rmtree
from pathlib import Path
from Adafruit_PureIO.smbus import SMBus

from .gps import GPSDLogger
from .mpl import MPLLogger
from .mpu import AccelRange, GyroRange, MPULogger


def create_session_folder():
    largest = 0

    session_logs = Path("/var/local/datalogger/session_logs")
    session_logs_current = session_logs / "current"

    if session_logs_current.exists():
        # Compress old logs
        zips = [file.name for file in session_logs.iterdir() if file.name.endswith(".zip")]
        largest = max((int(file[:-4]) for file in zips), default=0)
        filename = f"{largest + 1:04}.zip"

        print(f"Compressing previous logs to {filename}")
        start = time.monotonic()
        ret = call(("zip", "-1", "-r", "-j", filename, session_logs_current), cwd=session_logs)
        print(f"Finished compressing in {time.monotonic() - start:.02f}s (return code {ret})")
        rmtree(session_logs_current)

    session_logs_current.mkdir(parents=True, exist_ok= True)
    print("Logging to", session_logs_current)

    return session_logs_current


async def main():
    session_folder = create_session_folder()

    bus = SMBus(3)

    await asyncio.gather(
        GPSDLogger(session_folder).start(),
        MPLLogger(session_folder, bus).start(),
        MPULogger(
            session_folder,
            bus,
            accel_range=AccelRange.RANGE_16_G,
            gyro_range=GyroRange.RANGE_1000_DPS,
        ).start(),
    )


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    asyncio.get_event_loop().close()
