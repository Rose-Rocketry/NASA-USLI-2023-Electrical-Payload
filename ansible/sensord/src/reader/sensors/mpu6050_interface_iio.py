from enum import Enum
from pathlib import Path
import iio


class MPU6050Interface:
    def __init__(
        self,
    ) -> None:
        self.dev = iio.Context().find_device("mpu6050")
        self.ch_ax = self.dev.find_channel("accel_x")
        self.ch_ay = self.dev.find_channel("accel_y")
        self.ch_az = self.dev.find_channel("accel_z")
        self.ch_gx = self.dev.find_channel("anglvel_x")
        self.ch_gy = self.dev.find_channel("anglvel_y")
        self.ch_gz = self.dev.find_channel("anglvel_z")

    # We can't use the normal buffer system since the interrupt pin isn't connected
    def read_channel_raw(self, channel: iio.Channel):
        return int(channel.attrs["raw"].value) * float(channel.attrs["scale"].value)

    def read_data(self):
        return {
            "accel": (
                self.read_channel_raw(self.ch_ax),
                self.read_channel_raw(self.ch_ay),
                self.read_channel_raw(self.ch_az),
            ),
            "gyro": (
                self.read_channel_raw(self.ch_gx),
                self.read_channel_raw(self.ch_gy),
                self.read_channel_raw(self.ch_gz),
            ),
        }
