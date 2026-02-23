# Pipeline Orchestration

The transition to the Envelope strategy turns the `Pipeline` into a standardized conveyor belt. Because the wrapping logic is moved into the Adapters and the "policing" logic into the Middleware ports, the `run()` method becomes cleaner and more type-safe.

---

## 1. Updated `Pipeline` Class

In the `run()` method, the `current_env` variable always holds an `Envelope` instance; only its internal state changes as it moves through the processor chain.

```python
# src/app/pipelines/base.py
from typing import List, Optional
from ..ports.datastream import DataStream
from ..ports.middleware import Middleware
from ..ports.envelope import Envelope

class Pipeline:
    def __init__(
        self, 
        source: DataStream, 
        sink: DataStream,
        processors: List[Middleware] = None
    ):
        self.source = source
        self.sink = sink
        self.processors = processors or []

    def run(self) -> None:
        """Orchestrates the flow of Envelopes between Source and Sink."""
        # 1. Open both streams using their context managers
        with self.source as src, self.sink as snk:
            
            # 2. Iterate through the source (now yielding Envelopes)
            for envelope in src.read():
                
                # 3. Pass the envelope through the middleware chain
                current_env: Optional[Envelope] = envelope
                
                for process in self.processors:
                    current_env = process(current_env)
                    
                    # If any middleware returns None, the chunk is dropped
                    if current_env is None:
                        break
                
                # 4. If the envelope survived the chain, hand it to the sink
                if current_env is not None:
                    snk.write(current_env)
```

---

## 2. Key Changes and Benefits

### Explicit Type Hinting
The `processors` list now explicitly expects subclasses of the `Middleware` port. This ensures that every processor follows the `__call__(envelope) -> envelope | None` contract.

### The Standardized Iterator
The loop `for envelope in src.read()` now receives the DTO immediately from the source. This ensures that the first middleware in the chain has access to source-level metadata (like `chunk_index` or `source_url`).

### Enhanced State Management
Renaming the tracking variable to `current_env` reflects that we are passing a container, not just naked data. In previous versions, the loop state could be a dictionary or raw bytes, making debugging difficult. Now, it is always an `Envelope`.

### The Sink Handshake
The entire `Envelope` is passed to the sink. This allows the Sink (e.g., `LocalFileStream`) to perform its own final validation (checking the regime) and use metadata for logging before unwrapping the payload and writing it to the filesystem.

---

## 3. Implementation Summary
The `Pipeline` remains clean and simple because it just passes one `Envelope` after another. The "heavy lifting" is distributed across the ports and adapters, ensuring a scalable and maintainable architecture on the Linux ProDesk.
