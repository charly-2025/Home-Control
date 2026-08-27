import os
import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
LOGIN_PATH = os.getenv("LOGIN_PATH", "/api/auth/login")
LOGIN_EMAIL = os.getenv("LOGIN_EMAIL")
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD")

session = requests.Session()
_logged_in = False


def login() -> bool:
    global _logged_in
    resp = session.post(
        f"{BACKEND_URL}{LOGIN_PATH}",
        json={"email": LOGIN_EMAIL, "password": LOGIN_PASSWORD},
        timeout=5,
    )
    resp.raise_for_status()
    _logged_in = True
    return True


def get(path: str) -> requests.Response:
    global _logged_in
    if not _logged_in:
        login()

    resp = session.get(f"{BACKEND_URL}{path}", timeout=5)
    if resp.status_code == 401:
        login()
        resp = session.get(f"{BACKEND_URL}{path}", timeout=5)

    resp.raise_for_status()
    return resp