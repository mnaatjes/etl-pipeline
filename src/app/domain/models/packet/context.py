# src/app/domain/models/context.py
from dataclasses import dataclass, field, replace
from typing import Any, Dict, List

@dataclass(frozen=True)
class PipelineContext:
    """Metadata container"""
    origin:str      # Original Source URI (fixed)
    current:str     # Current URI (mutable)
    trace_id:str    # 'Commit' Hash (fixed)
    history: List[str] = field(default_factory=list) # Lineage tracking
    metadata:Dict[str,Any] = field(default_factory=dict)

    def clone(self) -> 'PipelineContext':
        """Explicit 1:1 Copy"""
        return replace(self)

    def commit(self, **updates) -> 'PipelineContext':
        """Update metadata and copy Context"""
        new_metadata = self.metadata.copy()
        new_metadata.update(updates)
        return replace(self,metadata=new_metadata)

    def rebase(self, new_uri:str) -> 'PipelineContext':
        """Update lineage"""
        new_history = self.history.copy()
        new_history.append(self.current)
        return replace(self, current=new_uri, history=new_history)
