from pathlib import PosixPath as Path

SERVO_UPDATE_FREQ = 50  # Standard value for servos, increasing may damage them
SERVO_PWM_PERIOD = int(1e9 / SERVO_UPDATE_FREQ)
SERVO_PWM_PERIOD_MIN = SERVO_PWM_PERIOD * 0.99 # There is some amount of error, the chip can't represent all frequencies exactly
SERVO_PWM_PERIOD_MAX = SERVO_PWM_PERIOD * 1.01

PWM_CHIP_ID = 0

PWM_CHIP_PATH = Path(f"/sys/class/pwm/pwmchip{PWM_CHIP_ID}")
PWM_CHIP_PATH_EXPORT = PWM_CHIP_PATH / "export"
PWM_CHIP_PATH_UNEXPORT = PWM_CHIP_PATH / "unexport"


class PWMPort:
    def __init__(self, pin_num: int) -> None:
        self.pin_num = pin_num
        self.path = PWM_CHIP_PATH / f"pwm{self.pin_num}"

        if self.path.exists():
            with open(PWM_CHIP_PATH_UNEXPORT, "w") as f_export:
                print(self.pin_num, file=f_export)
        with open(PWM_CHIP_PATH_EXPORT, "w") as f_export:
            print(self.pin_num, file=f_export)
        
        assert self.path.exists(), f"PWM Port {pin_num} not found"

        with open(self.path / "period", "r") as f_period:
            self.period = int(f_period.read())


        self._duty_cycle_f = open(self.path / "duty_cycle", "wb", buffering=0) 
        self.set_on_time(0)

    def set_on_time(self, on_time_ms):
        duty_cycle = int(on_time_ms * 1e6)

        self._duty_cycle_f.seek(0)
        self._duty_cycle_f.write((str(duty_cycle) + "\n").encode())

    def set_on_frac(self, frac):
        duty_cycle = int(frac * self.period)

        self._duty_cycle_f.seek(0)
        self._duty_cycle_f.write((str(duty_cycle) + "\n").encode())

class Servo(PWMPort):
    def __init__(self, pin_num: int, inverted: bool = False) -> None:
        super().__init__(pin_num)
        self.inverted = inverted

        assert SERVO_PWM_PERIOD_MIN <= self.period <= SERVO_PWM_PERIOD_MAX, f"Unexpected period, check your device tree! {self.period}ns found, expected {SERVO_PWM_PERIOD}ns"

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
    def __init__(self, *servos: tuple[Servo]):
        self._servos = servos

    def set_power(self, power):
        for servo in self._servos:
            servo.set_power(power)

    def set_angle(self, angle):
        for servo in self._servos:
            servo.set_angle(angle)

    def stop(self):
        for servo in self._servos:
            servo.stop()
