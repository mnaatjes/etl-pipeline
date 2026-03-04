# src/app/domain/models/packet/flow.py
from enum import StrEnum

class FlowSignal(StrEnum):
    """
    Signalman for the Packet Lifecycle.
    
    Coordinates how the Pipeline Orchestrator and Middleware handle buffering.
    """
    ATOMIC = "ATOMIC"       # A single, complete unit. No buffering required.
    STREAM_START = "START"  # The first packet; triggers engine/buffer initialization.
    STREAM_DATA = "DATA"    # Intermediate chunk; triggers accumulation/processing.
    STREAM_END = "END"      # The "Flush" signal; triggers buffer emptying.
