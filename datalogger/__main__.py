import asyncio
from pathlib import Path
from Adafruit_PureIO.smbus import SMBus

from .gps import GPSDLogger
from .mpl import MPLLogger
from .mpu import AccelRange, GyroRange, MPULogger


def create_session_folder():
    largest = 0

    path = Path("session_logs")

    # Find the largest number folder that already exists
    if path.exists():
        past_sessions = path.iterdir()
        largest = max((int(past_session.name) for past_session in past_sessions if past_session.name.isnumeric()), default=0)
    
    # Create a folder one higher than that one
    session_path = path / f"{largest + 1:04d}"

    if session_path.exists():
        raise Exception("Path already exists?")

    print("Creating", session_path)
    session_path.mkdir(parents=True)

    return session_path


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
