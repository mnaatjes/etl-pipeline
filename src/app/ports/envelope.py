# src/app/ports/envelope.py
from uuid import uuid4
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
    regime: RegimeType|str = RegimeType.BYTES
    metadata: Dict[str, Any] = field(default_factory=dict)
    completeness: Completeness = Completeness.COMPLETE
    id: str = field(default_factory=lambda: str(uuid4())[:12]) # Collission prob 1:20,000,000; Supports 281Trillion