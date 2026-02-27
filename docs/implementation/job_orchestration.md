# Implementation: Job Orchestration and Middleware

This document details how the **Data Plane** operates, using "Jobs" to orchestrate data movement through middleware.

## The Job (Interactor) Pattern
In Clean Architecture, a **Job** (e.g., `LinearJob`) is an **Interactor**. It represents a discrete business action. It defines the "What," while the `StreamManager` defines the "Where."

### The Bridge Strategy
The Job relies on the `DataStream` interface (the Port). It does not know about the `StreamManager`. The `StreamManager` acts as a factory that provides the `DataStream` objects to the Job at runtime.

```python
# src/app/jobs/linear.py
from src.app.ports.datastream import DataStream
from typing import List, Callable

class LinearJob:
    """SRP: Orchestrates data movement between a source and a sink."""
    def __init__(self, source: DataStream, sink: DataStream, processors: List[Callable]):
        self.source = source
        self.sink = sink
        self.processors = processors

    def run(self):
        # Robust loop logic using the Context Manager protocol
        with self.source as src, self.sink as snk:
            # Execution logic...
            pass
```

## Middleware as Transformations
Middleware components (generators) are independent of the infrastructure. They process the **Envelope** and are passed to the Job as a list of "processors."

### The "Elite" User Interaction
The user experience is divided into a **Bootstrap Phase** and a **Management/Execution Phase**.

```python
# --- PHASE 1: BOOTSTRAP (Setup) ---
boot = Bootstrapper(AppConfig(env="prod"))
boot.add_protocol_settings("http", HttpSettings(retries=5))
manager = boot.build_manager()

# --- PHASE 2: EXECUTION ---
src = manager.get_stream("http://remote.api/data")
snk = manager.get_stream("file:///local/storage.json", as_sink=True)

job = LinearJob(
    source=src,
    sink=snk,
    processors=[auth_guard, json_decoder, schema_validator]
)
job.run()
```

## Why this follows SRP
- **Resolver:** Pure Math/Logic (Settings merging).
- **Registry:** Directory/Inventory (Mapping URIs to Adapters).
- **Manager:** Factory/Dispatcher (Creating Stream instances).
- **Bootstrapper:** Constructor/Assembler (System initialization).
- **Job:** Stateless Orchestrator (Moving data through middleware).
