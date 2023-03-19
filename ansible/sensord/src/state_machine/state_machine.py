from abc import ABC, abstractmethod
from numbers import Number
from typing import final
from queue import Queue
import threading
import time
import logging

class Event(ABC):
    pass

class EventAltitude(Event):
    altitude: Number

    def __init__(self, data: dict) -> None:
        self.timestamp = data["timestamp"]
        self.altitude = data["altitude"]
        assert isinstance(self.timestamp, Number)
        assert isinstance(self.altitude, Number) 

class EventIMU(Event):
    gravity: tuple[Number, Number, Number]

    def __init__(self, data: dict) -> None:
        self.timestamp = data["timestamp"]
        self.gravity = data["gravity"]
        assert isinstance(self.timestamp, Number)
        assert len(self.gravity) == 3

class EventAPRSPacket(Event):
    source: str
    dest: str
    info: str

    def __init__(self, data: dict) -> None:
        self.source = data["source"]
        self.dest = data["dest"]
        self.info = data["info"]
        assert isinstance(self.source, str)
        assert isinstance(self.dest, str)
        assert isinstance(self.info, str)

class EventStateChange(Event):
    pass

class EventUpdateTimer(Event):
    pass

class StateMachine(ABC):
    max_delay: float
    update_timer_feed: threading.Event
    last_state_change: float
    last_state_change_elapsed: float

    def __init__(self, min_update_rate: float) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.max_delay = 1 / min_update_rate
        self.update_timer_feed = threading.Event()
        self.last_state_change = None
        self.last_state_change_elapsed = None
        self._state = None
        self._event_queue = Queue()

    @final
    def handle_event(self, event: Event):
        self._event_queue.put(event)

    @abstractmethod
    def handle_event_impl(self, event: Event):
        pass

    def get_state(self):
        return self._state

    def set_state(self, state):
        if state != self._state:
            self.logger.info(f"Setting state to {repr(state)}")
            self._state = state
            self.handle_event(EventStateChange())

    def _feed_update_timer_daemon(self):
        while True:
            self.update_timer_feed.wait(self.max_delay)
            if self.update_timer_feed.is_set():
                self.update_timer_feed.clear()
            else:
                self.handle_event(EventUpdateTimer())
                self._event_queue.join()

    def run(self, initial_state):
        self.set_state(initial_state)

        threading.Thread(target=self._feed_update_timer_daemon, daemon=True)
        
        while True:
            event = self._event_queue.get()

            self.update_timer_feed.set()
            now = time.monotonic()

            if isinstance(event, EventStateChange) or self.last_state_change == None:
                self.last_state_change = now

            self.last_state_change_elapsed = now - self.last_state_change
            
            self.handle_event_impl(event)

            self._event_queue.task_done()
