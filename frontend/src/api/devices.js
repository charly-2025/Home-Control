const API = "/api/devices";

export async function getDevices() {
    const response = await fetch(API);
    return await response.json();
}

export async function toggleDevice(name) {
    await fetch(
        `${API}/${encodeURIComponent(name)}/toggle`,
        {
            method: "POST",
        },
    );
}