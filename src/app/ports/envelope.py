# src/app/ports/envelope.py
from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass
class Envelope:
    payload: Any
    regime: str  # e.g., "BYTES" or "OBJECT"
    metadata: Dict[str, Any] = field(default_factory=dict)