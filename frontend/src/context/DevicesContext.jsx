import { createContext, useContext, useEffect, useState } from "react";

import { getDevices, toggleDevice as toggleDeviceApi } from "../api/devices";
import { connect, disconnect } from "../websocket/socket";

const DevicesContext = createContext(null);

export function DevicesProvider({ children }) {
    const [devices, setDevices] = useState([]);

    useEffect(() => {
        getDevices().then(setDevices);

        connect((message) => {
            if (message.type !== "device_updated") {
                return;
            }

            setDevices((current) =>
                current.map((d) =>
                    d.friendly_name === message.device.friendly_name
                        ? { ...d, ...message.device }
                        : d
                )
            );
        });

        return () => {
            disconnect();
        };
    }, []);

    function toggleDevice(device) {
        const newState = device.state === "ON" ? "OFF" : "ON";

        setDevices((current) =>
            current.map((d) =>
                d.friendly_name === device.friendly_name
                    ? { ...d, state: newState }
                    : d
            )
        );

        toggleDeviceApi(device.friendly_name);
    }

    return (
        <DevicesContext.Provider value={{ devices, toggleDevice }}>
            {children}
        </DevicesContext.Provider>
    );
}

export function useDevices() {
    return useContext(DevicesContext);
}
