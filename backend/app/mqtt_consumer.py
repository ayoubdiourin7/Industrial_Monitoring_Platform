import json
import os
import time
from datetime import datetime, timezone

from paho.mqtt import client as mqtt
from sqlalchemy import text

from .database import SessionLocal
from .models import Reading


MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "factory/+/metrics")


def wait_for_database() -> None:
    for _ in range(30):
        try:
            with SessionLocal() as session:
                session.execute(text("SELECT 1"))
                return
        except Exception:
            time.sleep(2)
    raise RuntimeError("Database did not become ready in time.")


def on_connect(client: mqtt.Client, _userdata, _flags, reason_code, _properties) -> None:
    if reason_code == 0:
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to MQTT topic: {MQTT_TOPIC}")
    else:
        print(f"MQTT connection failed with code: {reason_code}")


def on_message(_client: mqtt.Client, _userdata, message: mqtt.MQTTMessage) -> None:
    payload = json.loads(message.payload.decode("utf-8"))
    timestamp = datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00"))

    reading = Reading(
        machine_id=payload["machine_id"],
        vibration=payload["vibration"],
        acoustic=payload["acoustic"],
        power_draw=payload["power_draw"],
        timestamp=timestamp.astimezone(timezone.utc),
    )

    with SessionLocal() as session:
        session.add(reading)
        session.commit()


def start_mqtt_consumer() -> None:
    wait_for_database()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="monitoring-backend")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
    client.loop_start()
