import json
import paho.mqtt.client as mqtt
import logging
import enum
import math
import os
from . import state_machine, vector
from .pwm_device import Servo, ServoGroup, PWMPort
from .parser import parse_aprs_commands
from typing import Callable, Optional
from collections import deque
from numbers import Number

logging.basicConfig(level=logging.INFO)

with open("/opt/git_status") as f:
    GIT_STATUS = f.read()

TOPIC_PREFIX = "sensors/"
TOPIC_STATE_CURRENT = "state_machine/state/current"
TOPIC_STATE_ALL = "state_machine/state/all"
TOPIC_STATE_SET = "state_machine/state/set"
MIN_UPDATE_RATE = 20

class States(enum.IntEnum):
    SETUP_OPEN_DOOR_HOLD = enum.auto()
    SETUP_OPEN_CLOSE_DOOR = enum.auto()
    SETUP_CLOSE_DOOR = enum.auto()
    SETUP_CHUTE_OPEN = enum.auto()
    SETUP_CHUTE_CLOSE = enum.auto()
    LAUNCHPAD = enum.auto()
    FLYING = enum.auto()
    DEPLOY_CHUTE = enum.auto()
    DEPLOY_CHUTE_WAIT = enum.auto()
    DEPLOY_LEGS = enum.auto()
    DEPLOY_LEGS_WAIT = enum.auto()
    ORIENT = enum.auto()
    DEPLOY_DOOR = enum.auto()
    DEPLOY_DOOR_WAIT = enum.auto()
    DEPLOY_ARM = enum.auto()
    DEPLOY_ARM_WAIT = enum.auto()
    APRS_LISTEN = enum.auto()
    EXECUTE_COMMANDS = enum.auto()
    DONE = enum.auto()
    KILL = enum.auto()
    SHUTDOWN = enum.auto()


# Launch and Landing Detection
LAUNCH_DETECT_ALTITUDE_DELTA = 500
FLYING_MIN_DURATION = 3 * 60
FLYING_STABLE_DURATION = 60
FLYING_STABLE_GAP_DURATION = 2
FLYING_STABLE_MAX_SPEED = 2

# Self-orientation
VECTOR_DOWN = (-1, 0, 0)
VECTOR_SIDE = (0, 0, 1)
ORIENT_SERVO = ServoGroup(Servo(4), Servo(10, inverted=True))
ORIENT_P = 0.5
ORIENT_K = 0.6
ORIENT_THRESHOLD = math.radians(5)
ORIENT_TIMEOUT = 8
ORIENT_LOCKOUT = math.radians(50)

# Deployment
DEPLOY_CHUTE_SERVO = Servo(8)
DEPLOY_CHUTE_ANGLE_OPEN = -90
DEPLOY_CHUTE_ANGLE_CLOSE = 90
DEPLOY_CHUTE_DURATION = 3
DEPLOY_CHUTE_WAIT = 3
DEPLOY_LEGS_CHANNEL_A = PWMPort(14)
DEPLOY_LEGS_CHANNEL_B = PWMPort(15)
DEPLOY_LEGS_POWER = 0.5
DEPLOY_LEGS_DURATION = 5  # On time of burn wire
DEPLOY_LEGS_WAIT = 5  # How long to wait after deploying to start orienting
DEPLOY_DOOR_SERVO = ServoGroup(Servo(9), Servo(5))
DEPLOY_DOOR_POWER = 1
DEPLOY_DOOR_DURATION = 3
DEPLOY_DOOR_WAIT = 2
DEPLOY_ARM_SERVO = Servo(6)
DEPLOY_ARM_ANGLE_STOW = 90
DEPLOY_ARM_ANGLE_DEPLOY = -15
DEPLOY_ARM_DURATION = 4
DEPLOY_ARM_WAIT = 2

# APRS
APRS_CALLSIGN = "KQ4CTL"


CLOSE_ON_EXIT = [
    DEPLOY_CHUTE_SERVO,
    ORIENT_SERVO,
    DEPLOY_LEGS_CHANNEL_A,
    DEPLOY_LEGS_CHANNEL_B,
    DEPLOY_DOOR_SERVO,
    DEPLOY_ARM_SERVO
]


class RocketStateMachine(state_machine.StateMachine):
    initial_alt: Number
    stable_since: Number
    stable_deque: deque[state_machine.EventAltitude]
    emit_state_change: Callable[[States], None]
    last_received_commands: Optional[list[str]]

    def __init__(self) -> None:
        super().__init__(MIN_UPDATE_RATE)

        self.initial_alt = None
        self.stable_since = None
        self.stable_deque = None
        self.emit_state_change = None
        self.last_received_commands = None

    def handle_event_impl(self, event: state_machine.Event):
        state = self.get_state()

        if isinstance(event, state_machine.EventStateChange):
            self.emit_state_change(state)

        if state == States.SETUP_OPEN_DOOR_HOLD or state == States.SETUP_OPEN_CLOSE_DOOR:
            if isinstance(event, state_machine.EventStateChange):
                self.logger.info(f"Setup: Opening Door")
                DEPLOY_DOOR_SERVO.set_power(DEPLOY_DOOR_POWER)

            if self.last_state_change_elapsed > 5:
                if state == States.SETUP_OPEN_DOOR_HOLD:
                    DEPLOY_DOOR_SERVO.stop()
                    self.set_state(States.DONE)
                else:
                    self.set_state(States.SETUP_CLOSE_DOOR)

        elif state == States.SETUP_CLOSE_DOOR:
            if isinstance(event, state_machine.EventStateChange):
                self.logger.info(f"Setup: Closing Door")
                DEPLOY_DOOR_SERVO.set_power(-DEPLOY_DOOR_POWER)

            if self.last_state_change_elapsed > 0.5:
                DEPLOY_DOOR_SERVO.stop()
                self.set_state(States.DONE)

        elif state == States.SETUP_CHUTE_OPEN:
            if isinstance(event, state_machine.EventStateChange):
                self.logger.info(f"Setup: Opening Chute")
                DEPLOY_CHUTE_SERVO.set_power(DEPLOY_CHUTE_ANGLE_OPEN)

            if self.last_state_change_elapsed > DEPLOY_CHUTE_DURATION:
                DEPLOY_CHUTE_SERVO.stop()
                self.set_state(States.DONE)

        elif state == States.SETUP_CHUTE_CLOSE:
            if isinstance(event, state_machine.EventStateChange):
                self.logger.info(f"Setup: Closing Chute")
                DEPLOY_CHUTE_SERVO.set_power(DEPLOY_CHUTE_ANGLE_CLOSE)

            if self.last_state_change_elapsed > DEPLOY_CHUTE_DURATION:
                DEPLOY_CHUTE_SERVO.stop()
                self.set_state(States.DONE)

        elif state == States.SETUP_CLOSE_DOOR:
            if isinstance(event, state_machine.EventStateChange):
                self.logger.info(f"Closing Door")
                DEPLOY_DOOR_SERVO.set_power(-DEPLOY_DOOR_POWER)

            if self.last_state_change_elapsed > 0.5:
                DEPLOY_DOOR_SERVO.stop()
                self.set_state(States.DONE)

        elif state == States.LAUNCHPAD:
            """
                Waiting on launch pad.
                Listens to altimeter for a rise in 500m (is it meters?)
                Next State: FLYING
                Prev State: None.
            """
            if isinstance(event, state_machine.EventStateChange):
                self.logger.info("Waiting for launch")

            if isinstance(event, state_machine.EventAltitude):
                if self.initial_alt == None:
                    self.initial_alt = event.altitude

                if event.altitude > (self.initial_alt + LAUNCH_DETECT_ALTITUDE_DELTA):
                    self.logger.info(f"Launch detected at t={event.timestamp}, altitude={event.altitude}, initial_alt={self.initial_alt}")
                    self.set_state(States.FLYING)

        elif state == States.FLYING:
            """
                In-Flight state.
                Listens to altimeter for a rise in 500m (is it meters?)
                Next State: DEPLOY_LEGS
                Prev State: None.
            """
            if isinstance(event, state_machine.EventStateChange):
                self.logger.info("Waiting for landing")
                self.stable_since = None
                self.stable_deque = deque()

            if isinstance(event, state_machine.EventAltitude):
                self.stable_deque.append(event)
                
                if event.timestamp - self.stable_deque[0].timestamp <= FLYING_STABLE_GAP_DURATION:
                    return
                
                last_event = self.stable_deque.popleft()

                rate_of_change = (event.altitude - last_event.altitude) / (event.timestamp - last_event.timestamp)

                if abs(rate_of_change) < FLYING_STABLE_MAX_SPEED:
                    if self.stable_since == None:
                        # We are now stable, start the timer
                        self.stable_since = event.timestamp
                else:
                    # We're not stable, reset the timer
                    self.stable_since = None

                # Are we stable and have we been stable long enough?
                stable = (
                    self.stable_since != None
                    and event.timestamp - self.stable_since > FLYING_STABLE_DURATION
                )
                min_time_passed = (
                    self.last_state_change_elapsed > FLYING_MIN_DURATION
                )

                if stable and min_time_passed:
                    self.logger.info(f"Landing detected at t={event.timestamp}, rate_of_change={rate_of_change}")
                    self.get_state(States.DEPLOY_CHUTE)

        elif state == States.DEPLOY_CHUTE:
            if isinstance(event, state_machine.EventStateChange):
                self.logger.info("Deploying chute")
                DEPLOY_CHUTE_SERVO.set_angle(DEPLOY_CHUTE_ANGLE_OPEN)

            if self.last_state_change_elapsed > DEPLOY_CHUTE_DURATION:
                DEPLOY_CHUTE_SERVO.stop()
                self.set_state(States.DEPLOY_CHUTE_WAIT)

        elif state == States.DEPLOY_CHUTE_WAIT:
            if self.last_state_change_elapsed > DEPLOY_CHUTE_WAIT:
                self.set_state(States.DEPLOY_LEGS)

        elif state == States.DEPLOY_LEGS:
            if isinstance(event, state_machine.EventStateChange):
                self.logger.info("Deploying legs")
                DEPLOY_LEGS_CHANNEL_A.set_on_frac(DEPLOY_LEGS_POWER)
                DEPLOY_LEGS_CHANNEL_B.set_on_frac(DEPLOY_LEGS_POWER)

            if self.last_state_change_elapsed > DEPLOY_LEGS_DURATION:
                DEPLOY_LEGS_CHANNEL_A.set_on_frac(0)
                DEPLOY_LEGS_CHANNEL_B.set_on_frac(0)
                self.set_state(States.DEPLOY_LEGS_WAIT)

        elif state == States.DEPLOY_LEGS_WAIT:
            if self.last_state_change_elapsed > DEPLOY_LEGS_WAIT:
                self.set_state(States.ORIENT)

        elif state == States.ORIENT:
                if isinstance(event, state_machine.EventIMU):
                    angle = vector.get_angle(event.gravity, VECTOR_DOWN, VECTOR_SIDE)
                    if self.last_state_change_elapsed > ORIENT_TIMEOUT:
                        if abs(angle) > ORIENT_LOCKOUT:
                            ORIENT_SERVO.stop()
                            self.logger.error("Orient lockout violated, aborting mission")
                            self.set_state(States.DONE)
                        else:
                            ORIENT_SERVO.stop()
                            self.logger.error("Orient timed out, continuing")
                            self.set_state(States.DEPLOY_DOOR)
                    elif abs(angle) > ORIENT_THRESHOLD:
                        power = angle * ORIENT_P + math.copysign(
                            ORIENT_K, angle
                        )
                        self.logger.info(f"Orient angle={angle}, power={power}")
                        ORIENT_SERVO.set_power(power)
                    else:
                        ORIENT_SERVO.stop()
                        self.logger.error("Orient succeeded")
                        self.set_state(States.DEPLOY_DOOR)
                    
        elif state == States.DEPLOY_DOOR:
            if isinstance(event, state_machine.EventStateChange):
                self.logger.info(f"Deploying Door")
                DEPLOY_DOOR_SERVO.set_power(DEPLOY_DOOR_POWER)

            if self.last_state_change_elapsed > DEPLOY_DOOR_DURATION:
                DEPLOY_DOOR_SERVO.stop()
                self.set_state(States.DEPLOY_DOOR_WAIT)

        elif state == States.DEPLOY_DOOR_WAIT:
            if self.last_state_change_elapsed > DEPLOY_DOOR_WAIT:
                self.set_state(States.DEPLOY_ARM)

        elif state == States.DEPLOY_ARM:
            if isinstance(event, state_machine.EventStateChange):
                self.logger.info(f"Deploying Arm")
            
            progress = min(1, self.last_state_change_elapsed / DEPLOY_ARM_DURATION)

            DEPLOY_ARM_SERVO.set_angle((1-progress) * DEPLOY_ARM_ANGLE_STOW + progress * DEPLOY_ARM_ANGLE_DEPLOY)

            if self.last_state_change_elapsed > DEPLOY_ARM_DURATION:
                self.set_state(States.DEPLOY_ARM_WAIT)

        elif state == States.DEPLOY_ARM_WAIT:
            if isinstance(event, state_machine.EventStateChange):
                DEPLOY_ARM_SERVO.set_angle(DEPLOY_ARM_ANGLE_DEPLOY)

            if self.last_state_change_elapsed > DEPLOY_ARM_WAIT:
                DEPLOY_ARM_SERVO.stop()
                self.set_state(States.APRS_LISTEN)

        elif state == States.APRS_LISTEN:
            if not isinstance(event, state_machine.EventAPRSPacket):
                return
            
            self.logger.info(f"APRS Packet received: {event.source}>{event.dest}:{event.info}")

            if event.dest != APRS_CALLSIGN:
                self.logger.warn(f"APRS packet not for {APRS_CALLSIGN}, ignoring")
                return
            
            try:
                commands = parse_aprs_commands(event.info)

                if len(commands) > 0:
                    if self.last_received_commands != None:
                        if self.last_received_commands == commands:
                            self.logger.info("Two matching packets received, executing")
                            self.set_state(States.EXECUTE_COMMANDS)
                        else:
                            self.logger.warn("Two packets had differing commands, ignoring")
                else:
                    self.logger.error("No valid commands found in APRS packet")
                
                self.last_received_commands = commands
            except Exception as e:
                self.logger.error("Error parsing APRS packet", exc_info=e)
        
        elif state == States.EXECUTE_COMMANDS:
            self.logger.info(f"Executing commands {self.last_received_commands}")

            # TODO: Actually execute the commands

            self.set_state(States.DONE)

        elif state == States.DONE:
            pass

        elif state == States.KILL:
            raise InterruptedError("Kill requested")

        elif state == States.SHUTDOWN:
            os.system("shutdown now")
            raise InterruptedError("Shutdown requested")

        else:
            raise RuntimeError(f"Unknown State {state}")


def on_mqtt_connect(client: mqtt.Client, _, flags, rc):
    client.subscribe(TOPIC_PREFIX + "mpl3115", qos=0)
    client.subscribe(TOPIC_PREFIX + "bno055", qos=0)
    client.subscribe(TOPIC_STATE_SET)


def on_mqtt_message(client: mqtt.Client, sm: RocketStateMachine, message: mqtt.MQTTMessage):
    if message.topic == TOPIC_STATE_SET:
        state = States(int(message.payload))
        logging.info(f"Got request to switch to state {state}")
        sm.set_state(state)
    elif message.topic.startswith(TOPIC_PREFIX):
        id = message.topic.removeprefix(TOPIC_PREFIX)
        decoded = json.loads(message.payload)
        if "data" in decoded:
            data = decoded["data"]
            if id == "mpl3115":
                sm.handle_event(state_machine.EventAltitude(data))
            elif id == "bno055":
                sm.handle_event(state_machine.EventIMU(data))
            elif id == "aprs_packets":
                sm.handle_event(state_machine.EventAPRSPacket(data))

if __name__ == "__main__":
    print("State machine is starting")
    print("git status: " + GIT_STATUS)

    try:
        sm = RocketStateMachine()

        def emit_state_change(state):
            client.publish(TOPIC_STATE_CURRENT, int(state), retain=True)

        sm.emit_state_change = emit_state_change

        client = mqtt.Client("state-machine", clean_session=True, userdata=sm)
        client.on_connect = on_mqtt_connect
        client.on_message = on_mqtt_message
        client.enable_logger()
        client.connect("127.0.0.1")
        client.loop_start()

        client.publish(TOPIC_STATE_ALL, "\n".join((repr(a) for a in list(States))), retain=True)

        sm.run(States.LAUNCHPAD)
    finally:
        for pwm_device in CLOSE_ON_EXIT:
            try:
                pwm_device.close()
            except Exception as e:
                print(f"Error closing pwm device {pwm_device.path}: {e}")
