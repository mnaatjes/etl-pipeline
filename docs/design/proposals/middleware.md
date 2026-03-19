# Technical Specification: Packet-Processor Framework (2026)

This document contains the finalized Python implementations for the core entities of the StreamFlow refactor. These entities live in the **Domain Layer** and provide the "Smart" logic for transport-agnostic stream processing.

## 1. The `Packet` Entity (The Smart Unit of Work)
The `Packet` composes payload, type, signal, context, and identity into an immutable, lifecycle-aware message.

```python
from dataclasses import dataclass, field, replace
from typing import Any, Iterator, Optional

@dataclass(frozen=True)
class Packet:
    """
    The 'Smart Unit of Work' for the StreamFlow Framework.
    Composes payload, type, signal, context, and identity into a single movable unit.
    """
    # The 'What'
    payload: Any
    type: PayloadType = Subject.BYTES
    
    # The 'When'
    signal: FlowSignal = FlowSignal.ATOMIC
    
    # The 'Where/Why' (The Passport)
    context: PipelineContext = field(default=None)
    
    # The 'Who' (Lineage)
    identity: Identity = field(default_factory=Identity.start_chain)

    def __post_init__(self):
        """Ensure every Packet has a context upon creation."""
        if self.context is None:
            raise ValueError("Packet must be initialized with a PipelineContext.")

    # --- LIFECYCLE METHODS ---

    def is_flush_signal(self) -> bool:
        """Git: branch-end. Tells the Processor to empty its buffer."""
        return self.signal == FlowSignal.STREAM_END

    def is_stream(self) -> bool:
        """Check if this packet is part of a larger sequence."""
        return self.signal in (FlowSignal.STREAM_START, FlowSignal.STREAM_DATA, FlowSignal.STREAM_END)

    # --- DERIVATION METHODS (The 'Smart' Logic) ---

    def spawn(self, payload: Any, type: Optional[PayloadType] = None, signal: Optional[FlowSignal] = None) -> 'Packet':
        """
        Git: branch/commit. Creates a new Packet derivative.
        - Preserves the Context (The Passport)
        - Preserves the Correlation ID (The Lineage)
        - Updates the Identity (Pointing back to this Packet as parent)
        """
        return Packet(
            payload=payload,
            type=type or self.type,
            signal=signal or self.signal,
            context=self.context.clone(),
            identity=self.identity.spawn()
        )

    def drop(self) -> Iterator['Packet']:
        """Syntactic sugar for 'Swallowing' a packet."""
        return iter([])

    # --- PROXY METHODS (Direct access to Context) ---

    def commit(self, **metadata) -> 'Packet':
        """Git: commit. Proxy to update the underlying context metadata."""
        return replace(self, context=self.context.commit(**metadata))

    def rebase(self, new_uri: str) -> 'Packet':
        """Git: rebase. Proxy to update the data's current physical location."""
        return replace(self, context=self.context.rebase(new_uri))
```

## 2. The `MiddlewareProcessor` Abstraction (The Port)
A unified, polymorphic interface for all transformations, aggregations, and filters.

```python
from abc import ABC, abstractmethod
from typing import Iterator

class MiddlewareProcessor(ABC):
    """The Unified Port for all Pipeline Transformations."""
    
    @abstractmethod
    def process(self, packet: Packet) -> Iterator[Packet]:
        """Core logic for transformation/accumulation."""
        pass

    @abstractmethod
    def flush(self) -> Iterator[Packet]:
        """Drain hook triggered by FlowSignal.STREAM_END."""
        yield from []

    def open(self) -> None:
        """Resource initialization (e.g., DuckDB connection)."""
        pass

    def close(self) -> None:
        """Resource cleanup."""
        pass

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
```

## 3. Supporting Domain Entities

### `FlowSignal` (flow.py)
```python
from enum import StrEnum

class FlowSignal(StrEnum):
    ATOMIC = "ATOMIC"
    STREAM_START = "START"
    STREAM_DATA = "DATA"
    STREAM_END = "END"
```

### `PipelineContext` (context.py)
```python
@dataclass(frozen=True)
class PipelineContext:
    origin: str      
    current: str     
    trace_id: str    
    history: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def clone(self) -> 'PipelineContext':
        return replace(self)

    def commit(self, **updates) -> 'PipelineContext':
        new_meta = self.metadata.copy()
        new_meta.update(updates)
        return replace(self, metadata=new_meta)

    def rebase(self, new_uri: str) -> 'PipelineContext':
        new_history = self.history.copy()
        new_history.append(self.current)
        return replace(self, current=new_uri, history=new_history)
```

### `Identity` (identity.py)
```python
@dataclass(frozen=True)
class Identity:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    parent_id: Optional[str] = None

    @classmethod
    def start_chain(cls) -> 'Identity':
        root_id = str(uuid.uuid4())[:12]
        return cls(id=root_id, correlation_id=root_id)

    def spawn(self) -> 'Identity':
        return Identity(
            correlation_id=self.correlation_id,
            parent_id=self.id
        )
```

### `PayloadType` & `Subject` (payload.py)
```python
PayloadType = NewType("PayloadType", str)

class Subject:
    BYTES = PayloadType("binary:bytes")
    JSON  = PayloadType("document:json")
    DICT  = PayloadType("object:python-dict")
    CHUNK = PayloadType("stream:chunk")
    VOID  = PayloadType("system:void")
```
