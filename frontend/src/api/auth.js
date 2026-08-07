const API_URL = "/api";

export async function login(
    email,
    password,
) {

    const response = await fetch(
        `${API_URL}/auth/login`,
        {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                email,
                password,
            }),
        },
    );

    if (!response.ok) {
        throw new Error(await response.text());
    }

}

export async function register(data) {

    const response = await fetch(
        `${API_URL}/auth/register`,
        {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        },
    );

    if (!response.ok) {
        throw new Error(await response.text());
    }

}

export async function logout() {

    const response = await fetch(
        `${API_URL}/auth/logout`,
        {
            method: "POST",
            credentials: "include",
        },
    );

    if (!response.ok) {
        throw new Error(await response.text());
    }

}