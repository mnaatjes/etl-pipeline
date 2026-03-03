# src/app/domain/models/identity.py
from uuid import uuid4
from dataclasses import dataclass, field
from typing import Optional

@dataclass(frozen=True)
class Identity:
    """Lineage and trace for every unit of work"""
    id:str = field(default_factory=lambda: str(uuid4())[:12]) # Commit Hash
    stream_id:str = field(default_factory=lambda: str(uuid4())[:12]) # Persistend Hash for whole stream
    parent_id: Optional[str] = None # Parent Commit

    @classmethod
    def start(cls) -> 'Identity':
        """Creates the root-identity for the stream and packet"""
        root_id = str(uuid4())[:12]
        return cls(
            id=root_id,
            stream_id=root_id
        )
    
    def spawn(self) -> 'Identity':
        """Creates a new UUID for derivative and preserves stream_id"""
        return Identity(
            stream_id=self.stream_id,
            parent_id=self.id
        )