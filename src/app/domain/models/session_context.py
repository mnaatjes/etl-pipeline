# src/app/domain/models/session_context.py
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, Any, NewType

# -- Define Type: TraceID for Enforcement ---
TraceID = NewType("TraceID", str)

# --- Session Context Dataclass ---
@dataclass(frozen=True)
class SessionContext:
    trace_id: TraceID
    overrides: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    is_refined: bool = False

    def spawn(self, **call_overrides) -> 'SessionContext':
        """
        Refined the current context for a specific call
        - Merges session-level overrides with call-level overrides
        - Marks the context as is_refined=True
        - Generates new Timestamp
        """
        # Merge the directories (Call-level wins)
        merged = {**self.overrides, **call_overrides}
        return SessionContext(
            trace_id=self.trace_id,
            overrides=merged,
            created_at=datetime.now(),
            is_refined=True
        )