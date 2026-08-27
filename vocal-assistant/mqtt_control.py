import json
import os
import threading
import time
import paho.mqtt.client as mqtt

MQTT_HOST = os.getenv("MQTT_HOST", "mqtt")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

_lock = threading.Lock()
_waiters = {}
_last_payloads = {}


def _on_message(c, userdata, msg):
    with _lock:
        _last_payloads[msg.topic] = msg.payload.decode()
        waiter = _waiters.get(msg.topic)
        if waiter:
            waiter.set()


client.on_message = _on_message


def connect():
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    client.loop_start()


def send_and_confirm(topic_set: str, payload: dict, topic_state: str, field: str, expected: str, timeout=3.0) -> bool:
    event = threading.Event()
    with _lock:
        _waiters[topic_state] = event
    client.subscribe(topic_state)
    client.publish(topic_set, json.dumps(payload), qos=1)

    confirmed = False
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not event.wait(timeout=max(0, deadline - time.time())):
            break
        with _lock:
            actual = json.loads(_last_payloads.get(topic_state, "{}")).get(field)
        if str(actual) == str(expected):
            confirmed = True
            break
        event.clear()

    with _lock:
        _waiters.pop(topic_state, None)
    client.unsubscribe(topic_state)
    return confirmed