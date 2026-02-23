# Envelope Pattern Implementation

The Envelope DTO is a Data Contract representing the unified language spoken by Source, Middleware, and Sink. In this architecture, it belongs in `src/app/ports/envelope.py`.

## 1. The Envelope (DTO) Implementation
Using a Python `dataclass` is the most efficient way to implement this, as it is lightweight and plays nicely with Linux memory management.

```python
from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass
class Envelope:
    payload: Any                 # The actual data (bytes or dict)
    regime: str                  # e.g., "BYTES" or "OBJECT"
    metadata: Dict[str, Any] = field(default_factory=dict)
```

---

## 2. Port Evolution (The "Flat" Approach)
The "Flat Approach" for the `DataStream` port uses Type Hinting as the soft enforcement and keeps the standard `read` and `write` names, ensuring transparency without complex internal hooks.

### Updated Port Strategy (`src/app/ports/datastream.py`)
In this version, the responsibility of wrapping and unwrapping data is moved into the adapters themselves.

```python
from abc import ABC, abstractmethod
from typing import Any, Iterator
from .envelope import Envelope

class DataStream(ABC):
    @abstractmethod
    def read(self) -> Iterator[Envelope]:
        """Implementation must yield Envelope objects."""
        yield from []

    @abstractmethod
    def write(self, envelope: Envelope) -> None:
        """Implementation must accept an Envelope and handle its payload."""
        pass
```

### Adapter Implementation Example (`src/infrastructure/streams/local.py`)
Move the wrapping logic directly into the specific adapter's read loop.

```python
def read(self) -> Iterator[Envelope]:
    while chunk := self._file.read(self._chunk_size):
        yield Envelope(
            payload=chunk,
            regime="BYTES",
            metadata={"path": str(self.path)}
        )

def write(self, envelope: Envelope) -> None:
    # Just grab the payload and go
    self._file.write(envelope.payload)
```

---

## 3. The Role of the Envelope

*   **The Payload (The "Baton")**: The value inside the `.payload` property changes (e.g., `bytes` to `dict` and back) as it moves down the pipeline.
*   **The Regime (The "Traffic Light")**: A label telling the next middleware what is currently inside the payload.
*   **The Metadata (The "Passport")**: Carries "data about the data" (line/chunk tracking, source attribution, integrity checksums, diagnostics) without polluting the actual payload.

### Lifecycle & Memory
A new `Envelope` object is created for every chunk read from the source. On a Linux ProDesk, this is highly efficient because Python is designed for short-lived objects. As soon as a chunk is written to the sink, its `Envelope` falls out of scope and memory is reclaimed.

---

## 4. Why the "Flat Approach"?
*   **Explicitness**: You see exactly what is being yielded in each adapter.
*   **Tracebacks**: Errors point directly to the implementation (e.g., `local.py:read`) rather than obscured parent class logic.
*   **Speed**: Faster debugging of configuration errors during `Pipeline.run()`.
