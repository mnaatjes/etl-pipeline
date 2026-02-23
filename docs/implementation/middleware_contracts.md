# Middleware Contracts and Type Guarding

To enforce the Envelope strategy, the abstract middleware contracts shift their focus. Instead of validating "naked" data types (bytes vs. dict) as the primary input, they now validate the `Envelope.regime` and handle payload unwrapping/rewrapping automatically.

---

## 1. The Updated `Middleware` Port

Every middleware in the `Pipeline.run()` loop now receives a standardized `Envelope` object. This ensures access to `envelope.metadata` and `envelope.regime` at any point in the chain.

```python
# src/app/ports/middleware.py
from abc import ABC, abstractmethod
from .envelope import Envelope

class Middleware(ABC):
    """The absolute base for all pipeline processors."""
    @abstractmethod
    def __call__(self, envelope: Envelope) -> Envelope | None:
        """Receives an Envelope, returns an Envelope (or None to filter)."""
        pass
```

---

## 2. Regime-Specific Wrappers

The `ByteMiddleware` and `ObjectMiddleware` classes act as "Police" for the data regime, removing the need for repetitive `isinstance` checks in specific implementations.

### ByteMiddleware (Regime: `BYTES`)
*   **Guard**: Checks that `envelope.regime == "BYTES"`.
*   **Unpack**: Passes only the raw bytes to the `process()` method.
*   **Repack**: Updates the `envelope.payload` with the result and returns the envelope.

```python
class ByteMiddleware(Middleware):
    def __call__(self, envelope: Envelope) -> Envelope | None:
        if envelope.regime != "BYTES":
            raise TypeError(f"{self.__class__.__name__} expects 'BYTES' regime.")
        
        processed_payload = self.process(envelope.payload)
        if processed_payload is None: return None
            
        envelope.payload = processed_payload
        return envelope

    @abstractmethod
    def process(self, item: bytes) -> bytes | None:
        """Subclasses implement binary logic here."""
        pass
```

### ObjectMiddleware (Regime: `OBJECT`)
Follows the same pattern but enforces the `OBJECT` regime for structured data (dicts or lists).

---

## 3. The "Bridge" (Regime Changer)

A "Bridge" (like `JsonToBytes`) transitions data between regimes. Because it manually flips the regime switch, it inherits directly from the base `Middleware` class rather than the regime-specific wrappers.

```python
class JsonToBytes(Middleware):
    def __call__(self, envelope: Envelope) -> Envelope:
        if envelope.regime != "OBJECT":
            raise TypeError("JsonToBytes requires an OBJECT regime.")

        # Transform data and FLIP THE REGIME
        envelope.payload = json.dumps(envelope.payload).encode('utf-8')
        envelope.regime = "BYTES"
        
        return envelope
```

---

## 4. Key Benefits

*   **No Redundancy**: Type-checking logic is written once in the port, not in every middleware file.
*   **None/Filter Support**: Middleware can "drop" a chunk simply by returning `None`.
*   **Metadata Access**: Every middleware can read `envelope.metadata` (e.g., for logging) without being forced to manage it.
