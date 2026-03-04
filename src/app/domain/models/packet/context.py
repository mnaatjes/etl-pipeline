# src/app/domain/models/packet/context.py
from dataclasses import dataclass, field, replace
from typing import Any, Dict, List

@dataclass(frozen=True)
class PipelineContext:
    """
    The 'Where/Why' - Structured metadata and origin tracking.
    
    Acts as the 'Passport' for the data, containing trace information, 
    processing history, and arbitrary metadata.
    """
    origin: str      # Original Source URI
    current: str     # Current location/URI
    trace_id: str    # Unique ID for this specific pipeline execution
    history: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def clone(self) -> 'PipelineContext':
        """Creates an explicit 1:1 copy of the context."""
        return replace(self)

    def commit(self, **updates) -> 'PipelineContext':
        """
        Updates metadata and returns a new Context instance.
        """
        new_meta = self.metadata.copy()
        new_meta.update(updates)
        return replace(self, metadata=new_meta)

    def rebase(self, new_uri: str) -> 'PipelineContext':
        """
        Updates the current URI and adds the previous location to history.
        """
        new_history = self.history.copy()
        new_history.append(self.current)
        return replace(self, current=new_uri, history=new_history)
