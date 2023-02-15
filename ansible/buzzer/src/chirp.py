import gpiozero
from time import sleep

buz = gpiozero.PWMOutputDevice(18)


def chirp_ok():
    buz.frequency = 400
    buz.value = 0.3
    sleep(0.25)
    buz.value = 0


def chirp_error():
    buz.frequency = 100
    buz.value = 0.75
    sleep(0.5)
    buz.value = 0


def chirp_boot():
    buz.value = 0.5
    for i in range(10):
        buz.frequency = 100 + i * 50
        sleep(0.1)
    buz.value = 0


def chirp_shutdown():
    buz.value = 0.5
    for i in range(15):
        buz.frequency = 25 + (15 - i) * 50
        sleep(0.1)
    buz.value = 0


if __name__ == "__main__":
    chirp_boot()
    sleep(3)

    for i in range(3):
        chirp_ok()
        sleep(1.25)

    for i in range(5):
        chirp_error()
        sleep(0.5)

    chirp_shutdown()
