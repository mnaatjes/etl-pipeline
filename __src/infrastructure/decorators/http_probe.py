# src/infrastructure/decorators/http_probe.py
import httpx
from typing import Iterator

from src.app import DataStream
from src.app.ports.envelope import Envelope
from src.app.ports.decorator import Decorator

class HttpHeaderProbeDecorator(Decorator):

    def __init__(self, stream: DataStream):
        super().__init__(stream)
        self.headers = {}

    def open(self) -> None:
        # Perform pre-flight check
        try:
            with httpx.Client() as client:
                response = client.head(self._inner._resource_conf)
                self.headers = dict(response.headers)
        except httpx.RequestError as e:
            # Log error
            print(f"[WARNING] Header probe failed: {e}")

        # Implement Super
        super().open()

    def read(self) -> Iterator[Envelope]:
        # Intercept the read to inject metadata
        for envelope in super().read():
            # Ensure headers populated
            if self.headers:
                envelope.metadata.update(self.headers)
            # Yield packet
            yield envelope