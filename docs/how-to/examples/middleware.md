# Middleware Implementation Examples

By implementing the `MiddlewareProcessor` port, specific transformations become focused and type-safe.

---

## 1. The Secure Hasher (Binary Processor)
Calculates the SHA256 hash of chunks in a byte stream.

```python
# src/infrastructure/processors/security.py
import hashlib
from typing import Iterator
from src.app.ports.output.middleware_processor import MiddlewareProcessor
from src.app.domain.models.packet import Packet
from src.app.domain.models.packet.payload import PayloadSubject, PayloadType

class SHA256Hasher(MiddlewareProcessor):
    def __init__(self):
        self._sha256 = hashlib.sha256()

    @property
    def input_subject(self) -> PayloadType:
        return PayloadSubject.BYTES

    @property
    def output_subject(self) -> PayloadType:
        return PayloadSubject.BYTES

    def process(self, packet: Packet) -> Iterator[Packet]:
        # Process the binary payload
        self._sha256.update(packet.payload)
        
        # Yield the packet unchanged (we are just inspecting)
        yield packet

    def flush(self) -> Iterator[Packet]:
        # Optionally yield the final hash as a metadata packet or similar
        # For this example, we just finish.
        yield from []

    def get_hash(self) -> str:
        return self._sha256.hexdigest()
```

---

## 2. The Field Mapper (Object Processor)
Operates on structured dictionaries, transforming fields.

```python
# src/infrastructure/processors/transforms.py
from typing import Dict, Iterator
from src.app.ports.output.middleware_processor import MiddlewareProcessor
from src.app.domain.models.packet import Packet
from src.app.domain.models.packet.payload import PayloadSubject, PayloadType

class FieldRenameMapper(MiddlewareProcessor):
    def __init__(self, mapping: Dict[str, str]):
        self.mapping = mapping

    @property
    def input_subject(self) -> PayloadType:
        return PayloadSubject.DICT

    @property
    def output_subject(self) -> PayloadType:
        return PayloadSubject.DICT

    def process(self, packet: Packet) -> Iterator[Packet]:
        # Standard dictionary transformation logic
        original = packet.payload
        transformed = {self.mapping.get(k, k): v for k, v in original.items()}
        
        # Spawn a new packet with the transformed payload to maintain lineage
        yield packet.spawn(payload=transformed)
```

---

## 3. The "Bridge" (Regime Changer)
Converters are unique because they flip the regime switch. They inherit from the base `Middleware` to get full control over the `Envelope`.

```python
# src/app/middleware/encoders.py
import json
from ..ports.middleware import Middleware
from ..ports.envelope import Envelope

class JsonToBytes(Middleware):
    def __call__(self, envelope: Envelope) -> Envelope:
        # 1. Check the 'Before' state
        if envelope.regime != "OBJECT":
            raise TypeError(f"JsonToBytes requires OBJECT, got {envelope.regime}")

        # 2. Transform the payload
        envelope.payload = json.dumps(envelope.payload).encode('utf-8')
        
        # 3. Update the 'After' state (Flip the switch)
        envelope.regime = "BYTES"
        
        # 4. (Optional) Update metadata to reflect the change
        envelope.metadata["last_encoding"] = "utf-8"
        
        return envelope
```

---

## 4. The "Inspector" (Regime Neutral)
A passive middleware that peeks inside without changing anything.

```python
# src/app/middleware/telemetry.py
import logging
from ..ports.middleware import Middleware
from ..ports.envelope import Envelope

logger = logging.getLogger(__name__)

class PipelineInspector(Middleware):
    def __call__(self, envelope: Envelope) -> Envelope:
        logger.info(
            f"INSPECTOR: Regime={envelope.regime} | "
            f"Size={len(str(envelope.payload))} | "
            f"Index={envelope.metadata.get('chunk_index', 'N/A')}"
        )
        return envelope
```
