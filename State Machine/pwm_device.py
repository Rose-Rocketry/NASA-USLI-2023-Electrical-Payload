from pathlib import PosixPath as Path

SERVO_UPDATE_FREQ = 50  # Standard value for servos, increasing may damage them
SERVO_PWM_PERIOD = int(1e9 / SERVO_UPDATE_FREQ)

PWM_CHIP_ID = 0

PWM_CHIP_PATH = Path(f"/sys/class/pwm/pwmchip{PWM_CHIP_ID}")
PWM_CHIP_PATH_EXPORT = PWM_CHIP_PATH / "export"
PWM_CHIP_PATH_UNEXPORT = PWM_CHIP_PATH / "unexport"


class PWMPort:
    def __init__(self, pin_num: int) -> None:
        self.pin_num = pin_num
        self.path = PWM_CHIP_PATH / f"pwm{self.pin_num}"
        
        assert self.path.exists(), f"PWM Port {pin_num} not found"

        with open(self.path / "period", "r") as f_period:
            self.period = int(f_period.read())

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

        self.set_on_time(0)

    def close(self):
        self.stop()

        with open(PWM_CHIP_PATH_UNEXPORT, "w") as f_unexport:
            print(self.pin_num, file=f_unexport)

    def set_on_time(self, on_time_ms):
        duty_cycle = int(on_time_ms * 1e6)

        with open(self.path / "duty_cycle", "w") as f_duty_cycle:
            print(duty_cycle, file=f_duty_cycle)

    def set_on_frac(self, frac):
        duty_cycle = int(frac * self.period)

        with open(self.path / "duty_cycle", "w") as f_duty_cycle:
            print(duty_cycle, file=f_duty_cycle)

class Servo(PWMPort):
    def __init__(self, pin_num: int, inverted: bool = False) -> None:
        super().__init__(pin_num)
        self.inverted = inverted

        assert self.period == SERVO_PWM_PERIOD, f"Unexpected period, check your device tree! {self.period}ns found, expected {SERVO_PWM_PERIOD}ns"

    def set_power(self, power):
        """
        Power should be between -1 and 1
        """
        if self.inverted:
            power = -power
        power = max(-1, min(1, power))
        self.set_on_time(1.5 + (power * 0.5))

    def set_angle(self, angle):
        """
        Angle should be between -90 and 90
        """
        if self.inverted:
            power = -power
        on_time = 1 + (angle + 90) / 180
        self.set_on_time(on_time)

    def stop(self):
        self.set_on_time(0)


class ServoGroup:
    def __init__(self, servos: tuple[Servo]):
        self._servos = servos

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.close()
        return False

    def open(self):
        for servo in self._servos:
            servo.open()

    def close(self):
        for servo in self._servos:
            servo.close()

    def set_power(self, power):
        for servo in self._servos:
            servo.set_power(power)

    def set_angle(self, angle):
        for servo in self._servos:
            servo.set_angle(angle)

    def stop(self):
        for servo in self._servos:
            servo.stop()
