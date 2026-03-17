# src/app/domain/models/session_context.py

from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(frozen=True)
class SessionContext:
    trace_id: str
    overrides: Dict[str, Any] = field(default_factory=dict)