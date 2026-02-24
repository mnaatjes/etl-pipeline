# src/app/ports/envelope.py
from dataclasses import dataclass, field
from typing import Any, Dict, Literal

# Define Regimes
RegimeType = Literal["BYTES", "OBJECT"]

@dataclass
class Envelope:
    payload: Any
    regime: RegimeType
    metadata: Dict[str, Any] = field(default_factory=dict)