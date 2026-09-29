# -*- coding: utf-8 -*-
"""Вспомогательные функции."""
import time
import requests


def wait_for_server(base_url: str, timeout: float = 15, poll: float = 0.5) -> bool:
    """Ожидание готовности сервера (GET /api/v1/health)."""
    deadline = time.time() + timeout
    last_error = None
    while time.time() < deadline:
        try:
            response = requests.get(f"{base_url}/api/v1/health", timeout=2)
            if response.status_code == 200 and response.json().get("status") == "healthy":
                return True
        except requests.RequestException as exc:
            last_error = exc
        time.sleep(poll)
    raise RuntimeError(f"Server {base_url} is not available: {last_error}")
