import json
import asyncio

from app.websocket import websocket_manager
from app.mqtt import mqtt_client


class DeviceManager:

    def __init__(self):

        self.devices = {}

        mqtt_client.add_callback(
            "zigbee2mqtt/+",
            self.on_device_update,
        )

        mqtt_client.add_callback(
            "zigbee2mqtt/bridge/devices",
            self.on_devices,
        )
        
        
    def get_device_type(self, device: dict) -> str | None:

        definition = device.get("definition")

        if not definition:
            return None

        for expose in definition.get("exposes", []):

            expose_type = expose.get("type")

            if expose_type not in (
                "linkquality",
                "numeric",
                "binary",
                "enum",
            ):
                return expose_type

        return None


    def on_devices(
        self,
        topic: str,
        payload: str,
    ):

        devices = json.loads(payload)

        self.devices = {
            device["friendly_name"]: device
            for device in devices
        }

        for device in self.devices.values():

            if device["type"] == "Coordinator":
                continue

            mqtt_client.publish(
                f"zigbee2mqtt/{device['friendly_name']}/get",
                {
                    "state": ""
                },
            )

    def on_device_update(
        self,
        topic: str,
        payload: str,
    ):

        device_name = topic.split("/")[1]

        if device_name == "bridge":
            return

        if device_name not in self.devices:
            return

        try:
            data = json.loads(payload)
            print(f"MQTT RECV -> {device_name} | {data}")
        except json.JSONDecodeError:
            return

        self.devices[device_name].update(data)
        websocket_manager.broadcast_threadsafe(
            {
                "type": "device_updated",
                "device": self.devices[device_name],
            }
        )
    

    def get_devices(self):

        devices = []

        for device in self.devices.values():
            if device["type"] == "Coordinator":
                continue
            
            devices.append({
                "friendly_name": device["friendly_name"],
                "ieee_address": device["ieee_address"],
                "manufacturer": device.get("manufacturer"),
                "model": device.get("model_id"),
                "device_type": self.get_device_type(device),
                "zigbee_type": device["type"],
                "state": device.get("state"),
                "linkquality": device.get("linkquality"),
                "power_source": device.get("power_source"),
                "supported": device["supported"],
                "disabled": device["disabled"],
            })

        return devices

    def get_device(
        self,
        device_name: str,
    ):

        return self.devices.get(device_name)

    def turn_on(
        self,
        device_name: str,
    ):

        mqtt_client.publish(
            f"zigbee2mqtt/{device_name}/set",
            {
                "state": "ON",
            },
        )

    def turn_off(
        self,
        device_name: str,
    ):

        mqtt_client.publish(
            f"zigbee2mqtt/{device_name}/set",
            {
                "state": "OFF",
            },
        )
            
    def set_state(
        self,
        device_name: str,
        state: str,
    ):

        device = self.devices.get(device_name)

        if device is None:
            return None

        mqtt_client.publish(
            f"zigbee2mqtt/{device_name}/set",
            {
                "state": state,
            },
        )

        return device

    def toggle_state(
    self,
    device_name: str,
    ):

        device = self.devices.get(device_name)

        if device is None:
            return None

        current_state = device.get("state", "OFF")

        new_state = "OFF" if current_state == "ON" else "ON"

        mqtt_client.publish(
            f"zigbee2mqtt/{device_name}/set",
            {
                "state": new_state,
            },
        )

        return device

device_manager = DeviceManager()