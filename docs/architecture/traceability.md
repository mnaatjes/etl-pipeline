# Traceability Strategy: The `trace_id` Lifecycle

This document outlines the architecture of traceability within the **Slalom** framework, comparing the legacy implementation with the refined session-based approach.

---

## 1. What is the `trace_id`?

The `trace_id` is a **Correlation ID**. It is a unique, short-lived identifier (typically a 12-character UUID) that acts as the "Passport Number" for data as it moves through the system.

### Purpose:
- **Observability:** Link logs from different adapters (e.g., an HTTP read and a POSIX write) into a single logical "event."
- **Debugging:** If a pipeline fails midway, the `trace_id` allows an engineer to filter all system logs to see exactly what happened to that specific batch of data.
- **Context Awareness:** It allows the `StreamManager` to distinguish between multiple concurrent streams.

---

## 2. Legacy Flow (The "Repetitive" Pattern)

In the previous `StreamClient` implementation, the `trace_id` was resolved at initialization and then manually injected into every method call.

### Class Diagram (Old)
```mermaid
classDiagram
    class StreamClient {
        -str _trace_id
        +read(uri, **settings)
        +write(uri, data, **settings)
    }
    class StreamManager {
        +get_handle(uri, **overrides)
    }
    class TraceabilityProvider {
        +resolve(override)
    }

    StreamClient ..> TraceabilityProvider : resolves in __init__
    StreamClient --> StreamManager : calls with manual setdefault()
```

### Sequence Diagram (Old)
```mermaid
sequenceDiagram
    participant User
    participant SC as StreamClient
    participant SM as StreamManager

    User->>SC: read("local://file.dat")
    Note over SC: settings.setdefault("trace_id", self._trace_id)
    SC->>SM: get_handle(uri, **settings)
    Note over SM: overrides.pop("trace_id")
    SM-->>SC: StreamHandle (with trace_id)
    SC-->>User: Packets
```

**Critique:** Every single method in the Facade (`read`, `write`, `get_handle`, `pipeline`) had to remember to call `setdefault`. This led to code duplication and high risk of "trace-leak" (where a method forgets the ID and a new one is generated, breaking the chain).

---

## 3. Refactored Flow (The "Session Context" Pattern)

In the new `Flow` client, we treat the `trace_id` as part of a **Session Context**. The Facade centralizes the injection logic.

### Class Diagram (New)
```mermaid
classDiagram
    class Flow {
        -str _trace_id
        -_with_session(**overrides) Dict
        +read(uri, **settings)
        +pipeline(uri) PipelineBuilder
    }
    class PipelineBuilder {
        -str _trace_id
        +run()
    }
    class PipelineRunner {
        +execute_pipeline(trace_id)
    }

    Flow --> PipelineBuilder : spawns with session ID
    PipelineBuilder --> PipelineRunner : passes ID to run()
    Flow ..> StreamManager : proxies via _with_session()
```

### Sequence Diagram (New)
```mermaid
sequenceDiagram
    participant User
    participant F as Flow (Facade)
    participant PB as PipelineBuilder
    participant PR as PipelineRunner
    participant SM as StreamManager

    User->>F: pipeline("source.dat")
    F->>PB: new Builder(session_trace_id)
    User->>PB: run()
    PB->>PR: execute_pipeline(trace_id)
    PR->>SM: get_handle(trace_id)
    SM-->>F: StreamHandle (linked)
```

### Why this is better:
1.  **Centralized Logic:** The `_with_session` private helper ensures that any future session-level defaults (like `tenant_id` or `priority`) can be added in one place.
2.  **Explicit Contracts:** `PipelineBuilder` and `PipelineRunner` now take `trace_id` as an explicit argument rather than hiding it in a "messy bag" of `**settings`.
3.  **Consistency:** The `Flow` client ensures that every resource interaction within its lifetime is logically linked.

---

## 4. Resolution Hierarchy

The `trace_id` is resolved using a **Coalescing Strategy** in `TraceabilityProvider.resolve()`:

1.  **Method Override:** If a user passes `trace_id="FIXED-ID"` to a specific `.read()` call, it wins.
2.  **Session Default:** The `trace_id` assigned to the `Flow` instance at startup.
3.  **Environment/System:** (Future) Trace IDs from environment variables or parent process headers.
4.  **Automatic Generation:** A fresh UUID if nothing else is provided.
