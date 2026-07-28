import queue
import threading
from dataclasses import asdict
from typing import Any

from .models import Event

class EventManager:
    def __init__(self):
        self._clients: list[queue.Queue[dict[str, Any]]] = []
        self._history: list[dict[str, Any]] = []

        self._lock = threading.Lock()

    def send(self, event: Event):
        data = asdict(event)

        with self._lock:
            clients = list(self._clients)
            self._history.append(data)

        for client in clients:
            client.put(data)

    def subscribe_with_history(
            self,
    ) -> tuple[
        queue.Queue[dict[str, Any]],
        list[dict[str, Any]],
    ]:
        client = queue.Queue()

        with self._lock:
            history = list(self._history)
            self._clients.append(client)

        return client, history

    def unsubscribe(self, client):
        with self._lock:
            if client in self._clients:
                self._clients.remove(client)