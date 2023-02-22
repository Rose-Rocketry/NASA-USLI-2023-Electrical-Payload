import json
import paho.mqtt.client as mqtt
import queue
import threading
import logging
import enum
import math
from servo import Servo
from time import sleep

logging.basicConfig(level=logging.INFO)

TOPIC_PREFIX = "sensors/"

data_queue: queue.Queue[tuple[str, dict]] = queue.Queue(10)


def on_mqtt_connect(client, _, flags, rc):
    client.subscribe(TOPIC_PREFIX + "mpl3115", qos=0)
    client.subscribe(TOPIC_PREFIX + "bno055", qos=0)


def on_mqtt_message(client, _, message: mqtt.MQTTMessage):
    id = message.topic.removeprefix(TOPIC_PREFIX)
    decoded = json.loads(message.payload)
    if 'data' in decoded:
        if data_queue.full():
            dropped_id, _ = data_queue.get_nowait()
            print(f"queue full, packet dropped: {dropped_id}")
            
        data_queue.put_nowait((id, decoded['data']))


client: mqtt.Client = None


def iter_packets(filter_for_id: str):
    while True:
        id, decoded = data_queue.get()

        if id != filter_for_id:
            continue

        yield decoded

def get_packet(filter_for_id: str):
    for packet in iter_packets(filter_for_id):
        return packet


def iter_spaced_pairs(gap, iterator):
    buffer = []
    for thing_2 in iterator:
        buffer.append(thing_2)
        if len(buffer) >= gap:
            thing_1 = buffer.pop(0)

            yield thing_1, thing_2

class States(enum.Enum):
    LAUNCHPAD = enum.auto()
    FLYING = enum.auto()
    LANDED = enum.auto()
    ORIENT = enum.auto()
    DONE = enum.auto()

LAUNCH_DETECT_ALTITUDE_DELTA = 500
FLYING_MIN_DURATION = 300
FLYING_STABLE_DURATION = 60
FLYING_STABLE_GAP = 10
FLYING_STABLE_MAX_SPEED = 2
VECTOR_DOWN = (0, 0, 1)
VECTOR_SIDE = (1, 0, 0)
ORIENT_STAGE1_POWER = 1
ORIENT_STAGE1_THRESHOLD = math.radians(90)
ORIENT_STAGE2_P = 0.25
ORIENT_STAGE2_K = 0.25
ORIENT_STAGE2_THRESHOLD = math.radians(1)

def dot(a, b):
    return sum(an * bn for an, bn in zip(a, b))

def minus(a, b):
    return tuple(an - bn for an, bn in zip(a, b))

def get_orient_angle():
    gravity = get_packet("bno055")['gravity']
    a = dot(gravity, VECTOR_SIDE)
    b = dot(gravity, VECTOR_DOWN)
    angle = math.atan2(a, b)
    print(f"angle={angle}")
    return angle


def event_loop():
    # state = States.LAUNCHPAD
    state = States.ORIENT

    while True:
        if state == States.LAUNCHPAD:
            print("Waiting for launch")
            initial_alt = None
            for packet in iter_packets("mpl3115"):
                alt = packet["altitude"]

                if initial_alt == None:
                    initial_alt = packet["altitude"]

                if alt > (initial_alt + LAUNCH_DETECT_ALTITUDE_DELTA):
                    print(
                        f"Launch detected at t={packet['timestamp']}, alt={packet['altitude']}"
                    )
                    state = States.FLYING
                    break
        elif state == States.FLYING:
            initial_time = None
            
            print("Waiting for landing")
            stable_since = None

            for packet_1, packet_2 in iter_spaced_pairs(FLYING_STABLE_GAP, iter_packets("mpl3115")):
                if initial_time == None:
                    initial_time = packet_1['timestamp']

                rate_of_change = (packet_2["altitude"] - packet_1["altitude"]) / (
                    packet_2["timestamp"] - packet_1["timestamp"]
                )

                if abs(rate_of_change) < FLYING_STABLE_MAX_SPEED:
                    if stable_since == None:
                        # We are now stable, start the timer
                        stable_since = packet_2["timestamp"]
                else:
                    # We're not stable, reset the timer
                    stable_since = None

                # Are we stable and have we been stable long enough?
                stable = stable_since != None and packet_2['timestamp'] - stable_since > FLYING_STABLE_DURATION
                min_time_passed = packet_2['timestamp'] - initial_time > FLYING_MIN_DURATION

                if stable and min_time_passed:
                    print(f"Landing detected at t={packet_2['timestamp']}, rate_of_change={rate_of_change}")
                    state = States.LANDED
                    break
        elif state == States.LANDED:
            # TODO: Deploy Legs
            return
        elif state == States.ORIENT:
            with Servo(0) as s0:
                if(abs(get_orient_angle()) > ORIENT_STAGE1_THRESHOLD):
                    angle = get_orient_angle()

                    power = math.copysign(ORIENT_STAGE1_POWER, angle)
                    print(f"Orient stage 1, power={power}")
                    s0.set_power(power)

                    while abs(angle) > ORIENT_STAGE1_THRESHOLD:
                        angle = get_orient_angle()

                angle = get_orient_angle()
                while abs(angle) >= ORIENT_STAGE2_THRESHOLD:
                    angle = get_orient_angle()
                    power = angle * ORIENT_STAGE2_P + math.copysign(ORIENT_STAGE2_K, angle)
                    print(f"Orient stage 2, power={power}")
                    s0.set_power(power)
                
                print(f"Orient final angle: {math.degrees(angle)}")
                state = States.DONE
                    
        elif state == States.DONE:
            return
        else:
            raise RuntimeError(f"Unknown State {state}")


if __name__ == "__main__":
    client = mqtt.Client("state-machine", clean_session=True)
    client.on_connect = on_mqtt_connect
    client.on_message = on_mqtt_message
    client.enable_logger()
    client.connect("127.0.0.1")
    client.loop_start()
    event_loop()

