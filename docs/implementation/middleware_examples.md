# Middleware Implementation Examples

By inheriting from the updated `ByteMiddleware` and `ObjectMiddleware`, specific implementations become incredibly focused. They no longer worry about envelopes, regimes, or type-checking—they just do their specific job.

---

## 1. The Secure Hasher (Regime Preserver)
Calculates the hash of the payload but leaves the `Envelope` exactly as it found it.

```python
# src/app/middleware/security.py
import hashlib
from ..ports.middleware import ByteMiddleware

class SHA256Hasher(ByteMiddleware):
    def __init__(self):
        self._sha256 = hashlib.sha256()

    def process(self, item: bytes) -> bytes:
        # We only get here if envelope.regime was 'BYTES'
        self._sha256.update(item)
        
        # Returns bytes so the parent can repack them in the envelope
        return item

    def get_hash(self) -> str:
        return self._sha256.hexdigest()
```

---

## 2. The Field Mapper (Regime Preserver)
Operates on structured data, expecting an `OBJECT` regime and returning an `OBJECT` regime.

```python
# src/app/middleware/transforms.py
from typing import Dict
from ..ports.middleware import ObjectMiddleware

class FieldRenameMapper(ObjectMiddleware):
    def __init__(self, mapping: Dict[str, str]):
        self.mapping = mapping

    def process(self, item: dict) -> dict:
        # Standard dictionary transformation logic
        return {self.mapping.get(k, k): v for k, v in item.items()}
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
