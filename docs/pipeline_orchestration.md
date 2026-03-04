# Pipeline Orchestration & Middleware Design (Refactor 2026)

This document outlines the architectural patterns and interaction logic for the StreamFlow pipeline system. It defines how data moves through the system using the "Pipe and Filter" model, governed by a central Orchestrator.

## 1. The Core Metaphor: Librarian vs. Conductor

To maintain a strict Separation of Concerns, we distinguish between finding resources and executing logic:

*   **The StreamManager (The Librarian):** Responsible for URI resolution and adapter instantiation. It knows *where* the data is and *how* to connect to it.
*   **The PipelineOrchestrator (The Conductor):** Responsible for the execution flow. It knows the *order* of operations, manages the lifecycle of the middleware chain, and handles the "Handshake" between incompatible stages.

## 2. The Middleware Processor (The "Filter")

The `MiddlewareProcessor` is a stateful, lifecycle-aware port that transforms data.

### Interaction with Models
The processor is not a passive worker; it utilizes the "Smart" features of the `Packet` model:
- **Flow Control:** Inspects `Packet.signal` (START, DATA, END, ATOMIC) to manage internal buffers or state.
- **Lineage Maintenance:** Uses `Packet.spawn()` to create derivatives, ensuring the `Identity` (correlation ID) and `PipelineContext` (origin/history) are preserved across transformations.
- **Type Safety:** Declares its `input_subject` and `output_subject` (PayloadTypes) to ensure it only receives data it is equipped to handle.

### Contract (Methods & Properties)
- `name`: String identifier for telemetry and debugging.
- `input_subject` / `output_subject`: The "Handshake" declarations.
- `open()` / `close()`: Lifecycle hooks for resource management (e.g., DuckDB connections).
- `process(Packet) -> Iterator[Packet]`: The primary transformation logic.
- `flush() -> Iterator[Packet]`: Hook to drain buffers when a `STREAM_END` signal is received.

## 3. The Pipeline Orchestrator (The "Conductor")

The Orchestrator is the engine that drives the pipeline. It is responsible for the transition from a "Cold" configuration to a "Hot" execution.

### Responsibilities
1.  **Topological Validation (The Handshake):** Before execution, the Orchestrator traverses the chain to ensure the `output_subject` of stage N matches the `input_subject` of stage N+1.
2.  **Lifecycle Management:** Calls `open()` on all processors in the chain, ensures `process()` is called for every incoming packet, triggers `flush()` at the end of the stream, and guarantees `close()` is called on every component.
3.  **Memory Efficiency:** Adheres to a strict **Pipe and Filter** pattern using Python Iterators. This ensures that even with 200GB+ datasets, memory consumption remains constant (O(1)).
4.  **Error Propagation:** Provides a central point for catching and labeling errors (e.g., "Error in 'Validation Layer' while processing Packet ID: 123").

## 4. User API: The Fluent Builder

The `StreamClient` acts as the user's entry point, providing a clean, fluent interface that hides the complexity of the Orchestrator and Manager.

### Usage Pattern
```python
client = StreamClient()

pipeline = (
    client.pipeline("registry://raw/data.csv")  # Orchestrator initialization
    .pipe("json_parser")                       # Built-in selection
    .pipe(MyCustomFilter())                    # Custom instance injection
    .write("registry://processed/output.json") # Terminal operation
)

pipeline.run() # Execution & Validation
```

## 5. Architectural Standards

- **Hexagonal Integrity:** The Orchestrator (Application Layer) only depends on the `MiddlewareProcessor` port (Domain/Port Layer), never on concrete infrastructure implementations.
- **Immutability:** Packets are never modified in place. Processors must yield new instances via `spawn()`, `commit()`, or `rebase()`.
- **Lazy Evaluation:** No physical resource is opened until the `.run()` or terminal command is issued, allowing for pre-flight validation of the entire chain.
