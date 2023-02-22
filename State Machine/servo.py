from pathlib import PosixPath as Path

UPDATE_FREQ = 50  # Standard value for servos, increasing may damage them
PWM_PERIOD = int(1e9 / UPDATE_FREQ)

PWM_CHIP_ID = 0

PWM_CHIP_PATH = Path(f"/sys/class/pwm/pwmchip{PWM_CHIP_ID}")
PWM_CHIP_PATH_EXPORT = PWM_CHIP_PATH / "export"
PWM_CHIP_PATH_UNEXPORT = PWM_CHIP_PATH / "unexport"


class Servo:
    def __init__(self, pin_num: int) -> None:
        self.pin_num = pin_num
        self.path = PWM_CHIP_PATH / f"pwm{self.pin_num}"

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.close()
        return False

    def open(self):
        if self.path.exists():
            self.close()

        with open(PWM_CHIP_PATH_EXPORT, "w") as f_export:
            print(self.pin_num, file=f_export)

        assert self.path.exists()

        with open(self.path / "period", "w") as f_period:
            print(PWM_PERIOD, file=f_period)

        self.set_ms(0)

    def close(self):
        with open(PWM_CHIP_PATH_UNEXPORT, "w") as f_unexport:
            print(self.pin_num, file=f_unexport)

    def set_ms(self, duty_cycle):
        duty_cycle = int(duty_cycle * 1e6)

        with open(self.path / "duty_cycle", "w") as f_duty_cycle:
            print(duty_cycle, file=f_duty_cycle)  # 1.5ms

    def set_power(self, power):
        """
        Power should be between -1 and 1
        """
        power = max(-1, min(1, power))
        self.set_ms(1.5 + (power * 0.5))

    def stop(self):
        self.set_ms(0)
