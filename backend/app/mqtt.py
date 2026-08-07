import json
import time

import paho.mqtt.client as mqtt


class MQTTClient:

    def __init__(self):

        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2
        )

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        self.callbacks: dict[str, list] = {}

    def wait_for_connection(self):

        while True:

            try:

                self.client.connect(
                    "mqtt",
                    1883,
                    60,
                )

                self.client.loop_start()

                print("Connected to MQTT")

                return

            except Exception:

                print("Waiting for MQTT...")

                time.sleep(2)

    def disconnect(self):

        self.client.loop_stop()
        self.client.disconnect()

    def publish(
        self,
        topic: str,
        payload: dict | str,
    ):
        print(f"MQTT PUB -> {topic} | {payload}")
        if isinstance(payload, dict):
            payload = json.dumps(payload)

        self.client.publish(
            topic,
            payload,
        )

    def subscribe(
        self,
        topic: str,
    ):

        self.client.subscribe(topic)

    def add_callback(
        self,
        topic: str,
        callback,
    ):

        if topic not in self.callbacks:
            self.callbacks[topic] = []

        self.callbacks[topic].append(callback)

    def on_connect(
        self,
        client,
        userdata,
        flags,
        reason_code,
        properties=None,
    ):

        print("MQTT connected")

        for topic in self.callbacks:
            self.client.subscribe(topic)

    def on_disconnect(
        self,
        client,
        userdata,
        flags,
        reason_code,
        properties=None,
    ):

        print("MQTT disconnected")

    def on_message(
        self,
        client,
        userdata,
        msg,
    ):

        payload = msg.payload.decode()

        for topic, callbacks in self.callbacks.items():

            if mqtt.topic_matches_sub(
                topic,
                msg.topic,
            ):

                for callback in callbacks:

                    callback(
                        msg.topic,
                        payload,
                    )


mqtt_client = MQTTClient()