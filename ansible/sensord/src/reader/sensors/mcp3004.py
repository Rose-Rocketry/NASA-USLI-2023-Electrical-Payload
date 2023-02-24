from .sensor import PollingSensor
import iio
import os

# Calculated experientially, regression on y = k*x
LSB_VALUE = 1/26.875
MINIMUM_CELL_VOLTAGE = 3.3
MAXIMUM_CELL_VOLTAGE = 4.2
CELLS_SERIES = 2
MINIMUM_VOLTAGE = MINIMUM_CELL_VOLTAGE * CELLS_SERIES
MAXIMUM_VOLTAGE = MAXIMUM_CELL_VOLTAGE * CELLS_SERIES
CONSECUTIVE_UNDERVOLTAGE_SHUTDOWN = 10
CHANNEL_NAME = "voltage0"

class MCP3004Sensor(PollingSensor):
    def _get_sensor_id(self) -> str:
        return "battery"

    def _get_sensor_metadata(self):
        return {
            "name": "Battery",
            "channels": [
                {
                    "key": "voltage",
                    "name": "Battery Voltage",
                    "type": "number",
                    "unit": "V",
                    "minimum": MINIMUM_VOLTAGE,
                    "maximum": MAXIMUM_VOLTAGE,
                }
            ]
        }

    def _get_sensor_poll_rate(self) -> float:
        return 2

    def _run(self) -> None:
        self.dev = iio.Context().find_device("mcp3008")
        self.ch = self.dev.find_channel(CHANNEL_NAME)
        self.consecutive_undervoltages = 0

        return super()._run()

    def _poll(self) -> None:
        voltage = int(self.ch.attrs["raw"].value) * LSB_VALUE

        if voltage < MINIMUM_VOLTAGE:
            self._logger.warn(f"WARNING: BATTERY VOLTAGE OF {voltage:.2f}V IS BELOW MINIMUM {MINIMUM_VOLTAGE:.2f}V")
            self.consecutive_undervoltages += 1
            if self.consecutive_undervoltages > CONSECUTIVE_UNDERVOLTAGE_SHUTDOWN:
                self._logger.critical("SHUTTING DOWN SYSTEM")
                os.system("shutdown now")
                exit(0)
        else:
            self.consecutive_undervoltages = 0

        self.publish({
            "voltage": voltage
        })

SENSOR_CLASS = MCP3004Sensor
