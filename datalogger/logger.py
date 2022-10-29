from io import TextIOWrapper
from pathlib import Path
from re import S
from threading import Thread
import time

from .start_time import START_TIME


def fixed_str(x, length=10):
    if isinstance(x, float):
        return f"{x:{length}.0{length//2}f}"
    else:
        return str(x).rjust(length)


class Logger:
    log_file: TextIOWrapper
    name: str

    def __init__(self, session_folder: Path, name: str,
                 columns: tuple[str]) -> None:
        self.name = name

        log_path = session_folder / f"{name}.csv"
        self.log_file = open(log_path, "w", buffering=1)
        print(f"timestamp,", file=self.log_file, end="")
        print(",".join(columns), file=self.log_file)

    def log_values(self, *values: any):
        now = time.monotonic() - START_TIME
        h = now // 3600
        m = (now // 60) % 60
        s = now % 60
        now = f"{int(h):02d}:{int(m):02d}:{s:07.04f}"

        values_str = map(str, values)
        print(f"{now},", file=self.log_file, end="")
        print(",".join(values_str), file=self.log_file)

        print(f"[{self.name:>8} {now}]", end=" ")
        print(*map(fixed_str, values))

    async def start(self):
        raise NotImplementedError()
