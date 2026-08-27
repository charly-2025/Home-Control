import os
import auth

DEVICES_PATH = os.getenv("DEVICES_PATH", "/api/devices/")

DEVICE_TYPE_ACTIONS = {
    "switch": {
        "turn_on": {"payload": {"state": "ON"}, "expected_field": "state", "expected_value": "ON"},
        "turn_off": {"payload": {"state": "OFF"}, "expected_field": "state", "expected_value": "OFF"},
    },
    "cover": {
        "open": {"payload": {"state": "OPEN"}, "expected_field": "state", "expected_value": "OPEN"},
        "close": {"payload": {"state": "CLOSE"}, "expected_field": "state", "expected_value": "CLOSE"},
    },
}

def get_devices() -> dict:
    raw_devices = auth.get(DEVICES_PATH).json()
    devices = {}
    for dev in raw_devices:
        if dev.get("disabled") or not dev.get("supported", True):
            continue
        actions = DEVICE_TYPE_ACTIONS.get(dev["device_type"])
        if not actions:
            continue
        name = dev["friendly_name"]
        devices[name] = {
            "friendly_name": name,
            "device_type": dev["device_type"],
            "topic_set": f"zigbee2mqtt/{name}/set",
            "topic_state": f"zigbee2mqtt/{name}",
            "actions": actions,
        }
    return devices