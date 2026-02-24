# src/app/ports/envelope.py
from enum import Enum, StrEnum
from dataclasses import dataclass, field
from typing import Any, Dict, Literal

# Define Completeness for Buffering
class Completeness(Enum):
    PARTIAL = "partial"
    COMPLETE = "complete"
    BULK = "bulk"

# Define Regimes
class RegimeType(StrEnum):
    BYTES = "BYTES"
    OBJECT = "OBJECT"
    ANY = "ANY" # Wildcard for telemetry

@dataclass
class Envelope:
    payload: Any
    regime: RegimeType = RegimeType.BYTES
    metadata: Dict[str, Any] = field(default_factory=dict)
    completeness: Completeness = Completeness.COMPLETE