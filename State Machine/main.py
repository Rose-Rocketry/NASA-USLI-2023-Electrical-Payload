import json
import paho.mqtt.client as mqtt
import queue
import threading
import logging
import enum

logging.basicConfig(level=logging.INFO)

TOPIC_PREFIX = "sensors/"

data_queue_lock = threading.Lock()
data_queue: queue.Queue[mqtt.MQTTMessage] = None


def on_mqtt_connect(client, _, flags, rc):
    client.subscribe(TOPIC_PREFIX + "mpl3115", qos=0)
    # client.subscribe(TOPIC_PREFIX + "mpu6050", qos=0)


def on_mqtt_message(client, _, message: mqtt.MQTTMessage):
    id = message.topic.removeprefix(TOPIC_PREFIX)
    decoded = json.loads(message.payload)
    if data_queue != None:
        data_queue.put_nowait((id, decoded))


client: mqtt.Client = None


def iter_packets(filter_for_id: str):
    global data_queue

    with data_queue_lock:
        try:
            if data_queue != None:
                raise RuntimeError("iter_packets recursion detected")

            data_queue = queue.Queue[mqtt.MQTTMessage]()

            while True:
                id, decoded = data_queue.get()

                if id != filter_for_id:
                    continue

                yield decoded

        except GeneratorExit:
            data_queue = None
            return

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


LAUNCH_DETECT_ALTITUDE_DELTA = 500
FLYING_MIN_DURATION = 300
FLYING_STABLE_DURATION = 60
FLYING_STABLE_GAP = 10
FLYING_STABLE_MAX_SPEED = 2


def event_loop():
    state = States.LAUNCHPAD

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
            # TODO: Next Step
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

