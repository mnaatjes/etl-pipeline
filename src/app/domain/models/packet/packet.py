# src/app/domain/models/packet/packet.py
from dataclasses import dataclass, field, replace
from typing import Any, Iterator, Optional, cast

from src.app.domain.models.packet.flow import FlowSignal
from src.app.domain.models.packet.payload import PayloadType, Subject
from src.app.domain.models.packet.identity import Identity
from src.app.domain.models.packet.context import PipelineContext

@dataclass(frozen=True)
class Packet:
    """
    The 'Smart Unit of Work' for the StreamFlow Framework.
    
    Composes payload, type, signal, context, and identity into a 
    single, immutable, lifecycle-aware unit of work.
    """
    # The 'What'
    payload: Any
    type: PayloadType = Subject.BYTES
    
    # The 'When'
    signal: FlowSignal = FlowSignal.ATOMIC
    
    # The 'Where/Why' (The Passport)
    # We use Optional hint for the dataclass default, but cast it in methods
    context: Optional[PipelineContext] = None # type: ignore
    
    # The 'Who' (Lineage)
    identity: Identity = field(default_factory=Identity.start_chain)

    def __post_init__(self):
        """Ensure every Packet has a context upon creation."""
        if self.context is None:
            raise ValueError("Packet must be initialized with a PipelineContext.")

    # --- LIFECYCLE METHODS ---

    def is_flush_signal(self) -> bool:
        """Indicates whether this packet signals a buffer flush."""
        return self.signal == FlowSignal.STREAM_END

    def is_stream(self) -> bool:
        """Checks if this packet is part of a sequence of related packets."""
        return self.signal in (FlowSignal.STREAM_START, FlowSignal.STREAM_DATA, FlowSignal.STREAM_END)

    # --- DERIVATION METHODS (The 'Smart' Logic) ---

    def spawn(self, payload: Any, type: Optional[PayloadType] = None, signal: Optional[FlowSignal] = None) -> 'Packet':
        """
        Creates a new Packet derived from the current one.
        - Preserves the Context (The Passport)
        - Updates the Identity (Maintains Correlation ID, sets current as parent)
        """
        return Packet(
            payload=payload,
            type=type or self.type,
            signal=signal or self.signal,
            context=cast(PipelineContext, self.context).clone(),
            identity=self.identity.spawn()
        )

    def drop(self) -> Iterator['Packet']:
        """Syntactic sugar for 'Swallowing' a packet (terminating this branch)."""
        return iter([])

    # --- PROXY METHODS (Direct access to Context) ---

    def commit(self, **metadata) -> 'Packet':
        """Proxy to update the underlying context metadata."""
        return replace(self, context=cast(PipelineContext, self.context).commit(**metadata))

    def rebase(self, new_uri: str) -> 'Packet':
        """Proxy to update the current physical location in the context."""
        return replace(self, context=cast(PipelineContext, self.context).rebase(new_uri))
