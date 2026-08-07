import { apiFetch } from "./client";

export async function getCurrentUser() {
    const response = await apiFetch("/users/me");

    if (!response.ok) {
        throw new Error(await response.text());
    }

    return response.json();
}