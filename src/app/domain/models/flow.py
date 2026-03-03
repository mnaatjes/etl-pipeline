# src/app/domain/models/flow.py
from enum import StrEnum

class FlowSignal(StrEnum):
    """Signalman for Packet Lifecycle"""
    ATOMIC = "ATOMIC"       # Single, complete unit - no buffering
    STREAM_START = "START"  # Init engine/buffer
    STREAM_DATA = "DATA"    # Chunk
    STREAMEND = "END"       # Flush
