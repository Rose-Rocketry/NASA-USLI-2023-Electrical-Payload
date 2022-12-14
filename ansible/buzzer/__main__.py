# TODO Buzzer Service that listens to SystemD and offers
# Signals that can be used.

# Mido for midi tones
import signal
import os
import gpiozero.TonalBuzzer as Buzzer
from gpiozero.tones import Tone

class ShutdownGuard:
    """Allows for the buzzer to play a shutdown tone"""
    end_process = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.graceful_exit)


    def graceful_exit(self):
        self.end_process = True

class BuzzerController:
    """Controls and manages sounds for the buzzer.
       Once queue is done
    """
    def __init__(self, pin: int, guard: ShutdownGuard):
        self.guard = guard
        self.buzzer = Buzzer()
        self.tones = [] # A queue of (tone, duration) unions to play 

    def add_to_queue(self, list):
        self.tones.append(list)

    

if __name__ == "__main__":
    guard = ShutdownGuard()
    controller = BuzzerController(33, guard)