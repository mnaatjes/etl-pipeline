# Pipeline Subsystem: Execution Planning

**Date:** March 8, 2026
**Status:** Implementation Ready
**Scope:** Pipeline Builder, Runner, and Engine Orchestration

---

## 1. Core Architectural Roles

The system is organized into three distinct responsibilities to maintain Hexagonal integrity:

| Component | Responsibility | Analog | Layer |
| :--- | :--- | :--- | :--- |
| **`PipelineBuilder`** | **Configuration & Validation.** Collects the "What" (URIs, Processors). | The Architect | Application (Use Case) |
| **`PipelineRunner`** | **Orchestration.** Gets the engine, enters the context, and calls `.execute()`. | The Conductor | Application (Use Case) |
| **`PipelineEngine`** | **Execution.** The actual loop that moves packets from A to B. | The Worker | Infrastructure (Adapter) |

---

## 2. The Pipeline Builder (Fluent DSL)

### Responsibilities
- [x] **Identity Collection:** Aggregates source and sink URIs for Fan-in and Fan-out.
- [x] **Contract Adjudication:** Validates that the `output_subject` matches the `input_subject`.
- [x] **Blueprint Factory:** Transforms configuration state into an immutable `PipelineBlueprint`.
- [x] **Traceability Injection:** Integrated with `TraceabilityProvider`.

### Fluent Methods
- [x] `.pipeline(uri)`: Initial entry point (via `StreamClient`).
- [x] `.and_from(uri)`: Adds additional sources (Sequential Fan-in).
- [x] `.through(processor)`: Appends a `MiddlewareProcessor` and validates type compatibility.
- [x] `.to(uri)`: Adds a destination (Broadcast Fan-out).
- [x] `.run(engine_type)`: Terminal method; triggers orchestration.

---

## 3. Operational Logic & Edge Cases

### Fan-in / Fan-out
- **Fan-in:** Handled as a `List[str]` of source URIs. Default engine behavior is **Sequential** (Source A -> Close -> Source B) to prevent resource exhaustion.
- **Fan-out:** Handled as a `List[str]` of sink URIs. Default engine behavior is **Broadcast** (every packet is written to every sink).

### Safety & Constraints
- **Illegal Starts:** Prevented by requiring a source URI in the constructor.
- **Illegal Sinks:** `.run()` validates that at least one sink is defined via `.to()`.
- **Resource Management:** The `PipelineEngine` is the owner of the `with` blocks for all handles stored in the blueprint.

---

## 4. Risks & Mitigations

| Risk | Mitigation |
| :--- | :--- |
| **Linear Trap** | Blueprint uses lists for sinks to support broadcasting, laying the path for future DAG support without breaking the DSL. |
| **Circular Dependency** | `StreamClient` acts as the factory, injecting the `StreamManager` into the `PipelineBuilder` to break the cycle. |
| **Type Mismatch** | Builder performs "Contract Validation" at configuration time using `MiddlewareProcessor` port properties. |

---

## 5. User Journey (Big Picture)

1. User calls `client.pipeline()`.
2. `StreamClient` instantiates `PipelineBuilder` with `StreamManager` and `EngineRegistry`.
3. User chains configuration; Builder validates structural integrity.
4. User calls `.run()`.
5. Builder resolves handles, creates `PipelineBlueprint`, and hands off to `PipelineRunner`.
6. `PipelineRunner` selects the `PipelineEngine` and begins the execution loop.
