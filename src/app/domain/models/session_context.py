# src/app/domain/models/session_context.py

from dataclasses import dataclass, field
from typing import Dict, Any, NewType

# -- Define Type: TraceID for Enforcement ---
TraceID = NewType("TraceID", str)

# --- Session Context Dataclass ---
@dataclass(frozen=True)
class SessionContext:
    trace_id: TraceID
    overrides: Dict[str, Any] = field(default_factory=dict)