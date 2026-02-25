# src/app/ports/datastream.py (Add this helper)
from typing import Iterator
from .datastream import DataStream
from .envelope import Envelope

class Decorator(DataStream):
    """
    Abstract base for all DataStream Decorators.
    It delegates all calls to an 'inner' stream by default.
    """
    def __init__(self, stream: DataStream):
        # We initialize the base class using the inner stream's configuration
        super().__init__(
            resource_configuration=stream._resource_conf,
            chunk_size=stream._chunk_size,
            as_sink=stream._as_sink,
            policy=stream._policy,
            use_lines=stream._use_lines
        )
        self._inner = stream

    def open(self) -> None:
        self._inner.open()

    def read(self) -> Iterator[Envelope]:
        yield from self._inner.read()

    def write(self, envelope: Envelope) -> None:
        self._inner.write(envelope)

    def close(self) -> None:
        self._inner.close()

    def exists(self) -> bool:
        return self._inner.exists()