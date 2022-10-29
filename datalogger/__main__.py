import asyncio
from pathlib import Path
import shutil

from .gps import GPSDLogger
from .mpl import MPLLogger
from .mpu import MPULogger


def create_session_folder():
    # TODO: Generate a unique folder
    path = Path("session_logs")
    if path.exists():
        print("Deleting", path)
        shutil.rmtree(path)

    print("Creating", path)
    path.mkdir()

    return path


async def main():
    session_folder = create_session_folder()
    print(session_folder)

    await asyncio.gather(
        GPSDLogger(session_folder).start(),
        MPLLogger(session_folder).start(),
        MPULogger(session_folder).start(),
    )


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    asyncio.get_event_loop().close()
