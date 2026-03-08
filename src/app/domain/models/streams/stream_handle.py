# src/app/domain/models/streams/stream_handle.py
from typing import Iterator, Any, TYPE_CHECKING
from src.app.domain.models.streams.stream_capacity import StreamCapacity
from src.app.domain.models.streams.stream_context import StreamContext
from src.app.domain.models.packet.base import Packet

if TYPE_CHECKING:
    from src.app.ports.output.datastream import DataStream

class StreamHandle:
    """
    Dashboard for a DataStream
    - Provides introspection
    - Manages the lifecycle of a stream
    - Packet Factory

    """
    def __init__(self, adapter:'DataStream', capacity:StreamCapacity, context:StreamContext) -> None:
        # Define Props
        self._adapter   = adapter   # Worker
        self.capacity   = capacity  # Introspector
        self.context    = context   # Passport
        self.uri        = adapter.uri

    # --- PROPERTIES ---

    @property
    def is_open(self) -> bool:
        """Proxies the open state of the underlying adapter"""
        return self._adapter.is_open

    # --- ACTION METHODS ---

    def read(self) -> Iterator[Packet]:
        """
        Delegates reading to the Adapter.
        The Adapter already yields Self-Aware Packets stamped with Context.
        """
        if not self.is_open:
            raise IOError(f"Attempted to read from a closed stream: {self.uri}")
        
        yield from self._adapter.read()

    def write(self, payload: Any) -> None:
        """
        Guards writing with the capacity check.
        Wraps raw payload in a Packet before passing to adapter.
        """
        if not self.capacity.is_writable:
            raise PermissionError(f"Stream is read-only: {self.uri}")
        
        packet = Packet(payload=payload, context=self.context)
        self._adapter.write(packet)

    # --- CONTEXT MANAGER ---

    def __enter__(self) -> 'StreamHandle':
        self._adapter.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._adapter.__exit__(exc_type, exc_val, exc_tb)
