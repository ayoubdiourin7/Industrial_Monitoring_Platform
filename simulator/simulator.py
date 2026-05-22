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
    {"id": "press-01", "temperature": 72.0, "vibration": 2.0, "pressure": 31.0},
    {"id": "pump-02", "temperature": 68.0, "vibration": 1.4, "pressure": 28.0},
    {"id": "motor-03", "temperature": 75.0, "vibration": 2.5, "pressure": 35.0},
]


def generate_reading(machine: dict[str, float | str]) -> dict[str, float | str]:
    temperature = float(machine["temperature"]) + random.uniform(-1.5, 1.5)
    vibration = float(machine["vibration"]) + random.uniform(-0.3, 0.3)
    pressure = float(machine["pressure"]) + random.uniform(-1.0, 1.0)

    if random.random() < 0.08:
        vibration += random.uniform(2.5, 4.0)
        temperature += random.uniform(8.0, 18.0)

    return {
        "machine_id": machine["id"],
        "temperature": round(temperature, 2),
        "vibration": round(vibration, 2),
        "pressure": round(pressure, 2),
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
