# src/app/domain/models/streams/stream_capacity.py
from dataclasses import dataclass

@dataclass(frozen=True)
class StreamCapacity:
    can_seek:bool
    is_writable:bool
    supports_append:bool
    is_network:bool