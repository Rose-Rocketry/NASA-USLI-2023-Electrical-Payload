from .sensor import Sensor
from pathlib import Path
import paho.mqtt.client as mqtt
from kiss import TCPKISS, AX25KISSDecode


class OneShotLed:
    def __init__(self, name: str, brightness=1, delay_on=500, delay_off=500) -> None:
        self._path = Path("/sys/class/leds") / name

        with open(self._path / "trigger", "wt") as f:
            print("none", file=f)
        with open(self._path / "max_brightness") as f:
            max_brightness = int(f.read())
        brightness = int(max_brightness * brightness)
        with open(self._path / "brightness", "wt") as f:
            print(brightness, file=f)
        with open(self._path / "trigger", "wt") as f:
            print("oneshot", file=f)
        with open(self._path / "delay_on", "wt") as f:
            print(delay_on, file=f)
        with open(self._path / "delay_off", "wt") as f:
            print(delay_off, file=f)

        self.trigger()

    def trigger(self):
        with open(self._path / "shot", "wt") as f:
            print(1, file=f)


class KISSSensor(Sensor):
    def __init__(self, client: mqtt.Client) -> None:
        super().__init__(client)

    def _get_sensor_id(self) -> str:
        return "aprs_packets"

    def _get_sensor_metadata(self):
        return {
            "name": "APRS Packets",
            "channels": [
                {
                    "key": "source",
                    "name": "Source call sign",
                    "type": "string",
                },
                {
                    "key": "dest",
                    "name": "Destination call sign",
                    "type": "string",
                },
                {
                    "key": "info",
                    "name": "Message",
                    "type": "string",
                },
            ],
        }

    def _run(self):
        led = OneShotLed("led_b", 0.1)

        ki = TCPKISS("localhost", 8001)
        ki.start()

        decoder = AX25KISSDecode()

        while True:
            for frames in ki.read(min_frames=1):
                for frame in decoder.decode_frames(frames):
                    led.trigger()
                    self._logger.info(frame)
                    self._logger.info(
                        f"Packet from {frame.source} to {frame.destination}: {frame.info}"
                    )
                    self.publish(
                        {
                            "source": frame.source.callsign.decode("latin-1"),
                            "dest": frame.destination.callsign.decode("latin-1"),
                            "info": frame.info.decode(),
                        }
                    )


SENSOR_CLASS = KISSSensor
