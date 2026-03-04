# src/app/domain/models/streams/stream_handle.py
from typing import Iterator
from src.app.domain.models.streams.stream_capacity import StreamCapacity
from src.app.domain.models.streams.stream_context import StreamContext
from src.app.domain.models.packet.base import Packet
from src.app.ports.output.datastream import DataStream

class StreamHandle:
    """
    Dashboard for a DataStream
    - Provides introspection
    - Manages the lifecycle of a stream
    - Packet Factory

    """
    def __init__(self, adapter:DataStream, capacity:StreamCapacity, context:StreamContext) -> None:
        # Define Props
        self._adapter   = adapter   # Worker
        self.capacity   = capacity  # Introspector
        self.context    = context   # Passworp
        self.uri        = adapter._uri

    # --- PROPERTIES ---

    @property
    def is_open(self) -> bool:
        """Proxies the open state of the underlying adapter"""
        return self._adapter.is_open

    # --- ACTION METHODS ---

    def read(self) -> Iterator[Packet]:
        """
        Packet Factory: Deligates Reading to the Adapter
        - Ensures output is wrapped in Self-Aware Packets
        """
