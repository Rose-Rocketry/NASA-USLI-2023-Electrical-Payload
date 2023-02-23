import logging
from pathlib import Path
import logging
import humanize
import paho.mqtt.client as mqtt
import json
import json


def get_with_suffix(path: Path) -> Path:
    """
    Gets a non-existent path, adding a numbered suffix if needed
    """

    def generate_path(suffix: int):
        return path.parent / (path.name + "-" + str(suffix))

    suffix = 0
    new_path = generate_path(suffix)

    while new_path.exists():
        suffix += 1
        new_path = generate_path(suffix)

    return new_path


PREFIX = "sensors/"
LOG_FILE = open(get_with_suffix(Path("log.ndjson")), "at")

total = 0

def on_message(client, userdata, message: mqtt.MQTTMessage):
    id = message.topic.removeprefix(PREFIX)
    data = json.loads(message.payload)
    data["id"] = id

    line = json.dumps(data)
    print(line, file=LOG_FILE)

    global total
    total = total + 1

    if total % 200 == 0:
        logging.info(f"Logged {total} packets, {humanize.naturalsize(LOG_FILE.tell())}")


def main():
    logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger("main")
    client = mqtt.Client(client_id=f"sensord-logger", clean_session=True)
    client.enable_logger()

    logger.info("Starting MQTT Client")
    client.on_message = on_message
    client.connect("127.0.0.1")
    client.subscribe("sensors/#")
    client.loop_forever()


if __name__ == "__main__":
    main()
