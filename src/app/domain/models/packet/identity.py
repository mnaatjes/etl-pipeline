# src/app/domain/models/packet/identity.py
import uuid
from dataclasses import dataclass, field
from typing import Optional

@dataclass(frozen=True)
class Identity:
    """
    The 'Who' - Lineage and Traceability for every unit of work.
    
    Manages the parent-child relationship of packets as they move through 
    the transformation pipeline.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    parent_id: Optional[str] = None

    @classmethod
    def start_chain(cls) -> 'Identity':
        """
        Initializes a root identity.
        Both ID and Correlation ID are identical at the start of the chain.
        """
        root_id = str(uuid.uuid4())[:12]
        return cls(id=root_id, correlation_id=root_id)

    def spawn(self) -> 'Identity':
        """
        Creates a derivative identity.
        - Preserves Correlation ID (the lineage anchor).
        - Sets parent_id to the current ID.
        - Generates a new unique ID for the new unit.
        """
        return Identity(
            correlation_id=self.correlation_id,
            parent_id=self.id
        )
