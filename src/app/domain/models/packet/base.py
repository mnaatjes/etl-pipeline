# src/app/domain/models/packet/packet.py
from dataclasses import dataclass, field, replace
from typing import Any, Iterator, Optional, cast, Dict

from src.app.domain.models.packet.flow import FlowSignal
from src.app.domain.models.packet.payload import PayloadSubject, PayloadType
from src.app.domain.models.packet.identity import Identity
from src.app.domain.models.packet.completeness import Completeness
from src.app.domain.models.streams.stream_context import StreamContext

@dataclass(frozen=True)
class Packet:
    """
    The 'Smart Unit of Work' for the StreamFlow Framework.
    
    Composes payload, type, signal, context, and identity into a 
    single, immutable, lifecycle-aware unit of work.
    """
    # 1. CORE PROPERTIES
    payload: Any
    context: StreamContext

    # 2. LABELS
    subject: PayloadType = PayloadSubject.BYTES
    signal: FlowSignal = FlowSignal.ATOMIC
    completeness: Completeness = Completeness.COMPLETE

    metadata: Dict[str,Any] = field(default_factory=dict)
    identity: Identity = field(default_factory=Identity.start_chain)

    # --- LIFECYCLE METHODS ---

    def is_flush_signal(self) -> bool:
        """Indicates whether this packet signals a buffer flush."""
        return self.signal == FlowSignal.STREAM_END

    def is_stream(self) -> bool:
        """Checks if this packet is part of a sequence of related packets."""
        return self.signal in (FlowSignal.STREAM_START, FlowSignal.STREAM_DATA, FlowSignal.STREAM_END)

    # --- DERIVATION METHODS (The 'Smart' Logic) ---

    def spawn(
            self, 
            payload: Any, 
            subject: Optional[PayloadType] = None, 
            signal: Optional[FlowSignal] = None,
            completeness: Optional[Completeness] = None
    ) -> 'Packet':
        """
        Creates a new Packet derived from the current one.
        - Preserves the Context (The Passport)
        - Updates the Identity (Maintains Correlation ID, sets current as parent)
        """
        return Packet(
            payload=payload,
            subject=subject or self.subject,
            signal=signal or self.signal,
            completeness=completeness or self.completeness,
            context=self.context,
            identity=self.identity.spawn()
        )

    # --- PROXY METHODS (Direct access to Context) ---

    def commit(self, **metadata) -> 'Packet':
        """Proxy to update the underlying context metadata."""
        new_metadata = self.metadata.copy()
        new_metadata.update(metadata)
        return replace(self, metadata=new_metadata)

    def rebase(self, new_uri: str) -> 'Packet':
        """Proxy to update the current physical location in the context."""
        return replace(self, context=self.context.rebase(new_uri))

    def drop(self) -> Iterator['Packet']:
        """Syntactic sugar for 'Swallowing' a packet (terminating this branch)."""
        return iter([])