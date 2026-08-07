const API_URL = "/api";

async function refreshToken() {
    const response = await fetch(`${API_URL}/auth/refresh`, {
        method: "POST",
        credentials: "include",
    });

    return response.ok;
}

export async function apiFetch(
    path,
    options = {},
) {

    let response = await fetch(
        `${API_URL}${path}`,
        {
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                ...(options.headers || {}),
            },
            ...options,
        },
    );

    if (response.status !== 401) {
        return response;
    }

    const refreshed = await refreshToken();

    if (!refreshed) {
        window.location.href = "/login";
        throw new Error("Authentication failed");
    }

    response = await fetch(
        `${API_URL}${path}`,
        {
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                ...(options.headers || {}),
            },
            ...options,
        },
    );

    if (response.status === 401) {
        window.location.href = "/login";
        throw new Error("Authentication failed");
    }

    return response;
}