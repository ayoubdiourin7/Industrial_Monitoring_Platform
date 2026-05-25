import json
import os
import random
import time
from datetime import datetime, timezone

from paho.mqtt import client as mqtt


MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
MQTT_TOPIC_PREFIX = os.getenv("MQTT_TOPIC_PREFIX", "factory")
PUBLISH_INTERVAL_SECONDS = float(os.getenv("PUBLISH_INTERVAL_SECONDS", "1"))

MACHINES = [
    {"id": "press-01", "vibration": 2.1, "acoustic": 64.0, "power_draw": 18.0},
    {"id": "motor-02", "vibration": 1.6, "acoustic": 58.0, "power_draw": 12.5},
]


def generate_reading(machine: dict[str, float | str]) -> dict[str, float | str]:
    vibration = float(machine["vibration"]) + random.uniform(-0.3, 0.3)
    acoustic = float(machine["acoustic"]) + random.uniform(-2.5, 2.5)
    power_draw = float(machine["power_draw"]) + random.uniform(-0.8, 0.8)

    if random.random() < 0.08:
        vibration += random.uniform(2.5, 4.0)
        acoustic += random.uniform(10.0, 18.0)
        power_draw += random.uniform(3.0, 6.0)

    return {
        "machine_id": machine["id"],
        "vibration": round(vibration, 2),
        "acoustic": round(acoustic, 2),
        "power_draw": round(power_draw, 2),
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def main() -> None:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="machine-simulator")
    client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
    client.loop_start()

    while True:
        for machine in MACHINES:
            reading = generate_reading(machine)
            topic = f"{MQTT_TOPIC_PREFIX}/{machine['id']}/metrics"
            client.publish(topic, json.dumps(reading), qos=1)
            print(f"Published to {topic}: {reading}")
        time.sleep(PUBLISH_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
