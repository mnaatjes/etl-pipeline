# Pipeline Subsystem: Architectural Blueprint

This document defines the transition of the StreamFlow Pipeline subsystem from a prototype to a production-ready architectural implementation. It details the Engine Abstraction, Hexagonal placement, and integration strategy with the existing framework.

---

## 1. The PipelineEngine Port (The Contract)

The `PipelineEngine` is an **Output Port** that satisfies the Single Responsibility Principle (SRP) by focusing exclusively on the execution lifecycle and error boundary management.

### Properties
*   **`status: EngineState`**: An Enum (`IDLE`, `RUNNING`, `SUCCESS`, `FAILED`) representing the internal state machine of the executor.
*   **`trace_id: str`**: A unique identifier propagated from the `StreamContext` to correlate engine-level logs with a specific pipeline lifecycle.

### Methods
*   **`setup(blueprint: PipelineBlueprint)`**: Validates the "Job Ticket" (Source, Processors, Sink) before execution begins. Returns `self` to support context manager entry.
*   **`execute()`**: The primary data-plane loop. It is responsible for **Error Translation**, catching low-level infrastructure exceptions (e.g., `OSError`, `HTTPError`) and re-raising them as a domain-friendly `PipelineExecutionError`.
*   **`shutdown()`**: The **Resource Lifecycle** guard. Ensures all handles in the blueprint are closed, regardless of success or failure.
*   **`__enter__ / __exit__`**: Implements the Python Context Manager protocol to guarantee that `shutdown()` is called by the runtime, preventing resource leaks.

---

## 2. Hexagonal Tree Mapping

To maintain clean separation between domain logic and infrastructure implementation, the components are mapped as follows:

| Component | Layer | Path | Responsibility |
| :--- | :--- | :--- | :--- |
| **Engine Port** | Application (Output) | `src/app/ports/output/pipeline_engine.py` | The abstract interface/contract. |
| **Engine Registry** | Application (Registry) | `src/app/registry/engines.py` | The "Librarian" for pluggable engines. |
| **Trace Provider** | Domain (Service) | `src/app/domain/services/traceability_provider.py` | The SSoT for `trace_id` resolution. |
| **Pipeline Builder** | Application (Use Case) | `src/app/use_cases/pipeline_builder.py` | The Fluent DSL with Contract Adjudication. |
| **Pipeline Runner** | Application (Use Case) | `src/app/use_cases/pipeline_runner.py` | The "Conductor" coordinating the flow. |
| **Local Engine** | Infrastructure (Adapter)| `src/infrastructure/engines/local_engine.py` | Sequential/Broadcast implementation. |

---

## 3. The Lifecycle "Handshake"

The interaction between the user facade and the execution engine follows a strict sequence:

1.  **Initiation**: User calls `client.pipeline("uri")` via the `StreamClient`.
2.  **Definition**: `StreamClient` returns a `PipelineBuilder` (Use Case).
3.  **Construction**: User chains `.through().to()` on the builder to define the topology.
4.  **Selection**: User calls `.run(engine_type="local")`.
5.  **Resolution**: The Builder requests the "local" implementation from the `EngineRegistry`.
6.  **Handover**: The Builder creates a `PipelineBlueprint` and passes it to the Engine's `setup()` method.
7.  **Execution**: The Builder enters the Engine's context and calls `execute()`.
8.  **Cleanup**: The Engine's `__exit__` method automatically triggers `shutdown()`.

---

## 4. Architectural Review & Patterns

The subsystem employs several key design patterns to ensure flexibility and maintainability:

*   **Fluent Interface (Builder)**: Decouples the *definition* of the pipeline from its *execution*. It provides a human-readable DSL that reads like a sentence, improving Developer Experience (DX).
*   **Strategy Pattern (Engine)**: Decouples the *logic* of the pipeline (what happens to data) from the *mechanism* (how data moves). This allows the same pipeline to run locally, via multiprocessing, or on a distributed cluster without code changes.
*   **Registry Pattern**: Enables a "Pluggable" architecture. New execution engines can be registered into the framework at runtime, supporting future-proof scalability.
*   **Envelope Pattern (Packet)**: Ensures that data never travels "naked." Every unit of work carries its own context, lineage, and flow signals.

---

## 5. Integration with StreamManager

The Pipeline subsystem and the `StreamManager` have distinct but complementary roles:

*   **StreamManager (The Librarian)**: The authority on **Resources**. It handles resolution, security boundaries, and handle instantiation.
*   **PipelineRunner (The Conductor)**: The authority on **Workflows**. It coordinates the interaction between handles provided by the `StreamManager`.

**Integration Point**: The `PipelineBuilder` utilizes the `StreamManager` to resolve the URIs provided in the `.pipeline()` and `.to()` methods. Once the `StreamManager` provides a `StreamHandle`, the Builder "wraps" them into a `PipelineBlueprint` for the engine.

---

## 6. Rationalizing User Entry Points

To keep the `StreamClient` clean while expanding functionality, we organize entry points by **Intent**:

### A. The Facade (`StreamClient`)
The single point of entry for the user. It delegates to specialized managers:
- `client.get_handle()` -> Delegated to `StreamManager`.
- `client.pipeline()` -> Returns `PipelineBuilder`.

### B. Specialized Builders
As the framework grows, we will introduce new builders accessible via the `StreamClient`:
- `client.batch()`: For bulk data movement where latency is less critical than throughput.
- `client.watch()`: For reactive pipelines that trigger on resource changes (e.g., file system events).

### C. The Composition Root (`Bootstrap`)
The `Bootstrap` layer is responsible for "wiring" the `EngineRegistry` during startup. This ensures that the `StreamClient` is always equipped with a default `LocalEngine`, allowing users to simply call `.run()` without explicit configuration.
