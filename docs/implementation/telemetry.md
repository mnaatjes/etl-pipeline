# Telemetry and Pipeline Monitoring

In a streaming architecture, monitoring is achieved through **Passive Middleware** (Watchers or Observers). Because the pipeline treats every processor the same way, specialized monitoring components can be inserted anywhere in the chain to inspect the `Envelope` without modifying the payload or regime.

---

## 1. The "Pipeline Monitor" Pattern

A professional telemetry implementation uses the standardized metadata in the `Envelope` to track progress and state.

```python
# src/app/middleware/telemetry.py
import logging
from ..ports.middleware import Middleware
from ..ports.envelope import Envelope

logger = logging.getLogger(__name__)

class PipelineMonitor(Middleware):
    def __init__(self, name: str = "Default"):
        self.name = name
        self.total_bytes = 0

    def __call__(self, envelope: Envelope) -> Envelope:
        # Accessing standardized envelope properties
        size = envelope.metadata.get("bytes_read", 0)
        idx = envelope.metadata.get("chunk_index", "?")
        regime = envelope.regime
        
        self.total_bytes += size
        
        # Log the state of the "baton" as it passes this point
        logger.info(
            f"[{self.name}] Chunk {idx} | Regime: {regime} | "
            f"Size: {size}B | Total: {self.total_bytes}B"
        )
        
        # CRITICAL: Return the envelope untouched
        return envelope
```

---

## 2. Strategic Placement (Checkpoints)

The "Envelope" pattern allows monitors to be placed at different stages to observe regime transitions (e.g., from `BYTES` to `OBJECT`).

```python
processors = [
    PipelineMonitor(name="PRE-PROCESS"),   # Sees raw bytes from Source
    BytesToJson(),
    PipelineMonitor(name="POST-PARSE"),    # Sees dicts (regime changed!)
    FieldMapper(),
    JsonToBytes(),
    PipelineMonitor(name="PRE-SINK")       # Sees final bytes for disk
]
```

---

## 3. Global Monitoring in the Pipeline Loop

While middleware handles chunk-level telemetry, the `Pipeline.run()` loop can access the `Envelope` directly for global monitoring (e.g., progress bars).

```python
# src/app/pipelines/base.py

def run(self):
    with self.source as src, self.sink as snk:
        for envelope in src.read():
            # Access metadata for global context
            # print(f"Processing {envelope.metadata['source']}...")
            
            processed_envelope = envelope
            for process in self.processors:
                processed_envelope = process(processed_envelope)
                if processed_envelope is None:
                    break
            
            if processed_envelope is not None:
                snk.write(processed_envelope)
```

---

## 4. Best Practices & Constraints

*   **Avoid Modification**: A monitor must never change the payload. If it does, it is a transformation, not a monitor.
*   **Keep Logic Light**: Avoid database writes or heavy API calls inside `__call__`. Use local logging or in-memory counters to prevent bottlenecks.
*   **Use Logging Levels**: Prefer the `logging` module over `print` statements. This allows monitoring to be toggled via configuration without code changes.
*   **Context over Content**: Use monitors to verify that the "context" (metadata) matches the "content" (payload) at each stage.
