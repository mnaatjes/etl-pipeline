# Pipeline Project: Handoff & Status Report

**Current Date:** March 11, 2026
**Project:** StreamFlow (Pipeline Subsystem)

---

## 1. Project Context

The StreamFlow framework is built using a **Hexagonal Architecture** with **Domain-Driven Design (DDD)** principles. It provides a protocol-agnostic, context-aware data streaming engine. The current focus is implementing a high-performance, fluent **Pipeline Subsystem**.

### Core Concepts
- **Packet**: The smart unit of work carrying context and flow signals.
- **DataStream**: The output port for resource adapters (POSIX, HTTP).
- **StreamManager**: The orchestrator for individual resource resolution and handling.
- **PipelineRunner**: The singular orchestrator for multi-resource data-in-motion workflows.

---

## 2. Completed Milestones

We have completed the **Research and Strategy** phase for the Pipeline subsystem and have made significant progress in the **Implementation** phase, specifically establishing the application orchestration boundaries.

### Infrastructure & Domain
- [x] **`StreamCapacity` Update**: Added `is_readable` to the `StreamCapacity` dataclass to support explicit capability handshakes.
- [x] **`PipelineBlueprint` Domain Model**: Updated to support **Fan-in** (multiple sources) and **Fan-out** (multiple sinks) via list-based attributes. Act as the definitive "Job Ticket".
- [x] **`PipelineEngine` Port (Contract)**: Created `src/app/ports/output/pipeline_engine.py`. This abstract class defines the execution strategy, lifecycle (setup/execute/shutdown), and error translation.
- [x] **`TraceabilityProvider`**: Implemented a unified service for `trace_id` resolution and generation to ensure end-to-end observability across the facade, builder, and manager.
- [x] **`EngineRegistry`**: Implemented `src/app/registry/engines.py` to store and retrieve pluggable execution strategies.
- [x] **`AppContext` Refinement**: Refined `src/app/context.py` to correctly expose the "Resolution Stack" (Services/Registries) and "Orchestrators" (`StreamManager`, `PipelineRunner`) as a consolidated runtime container.
- [x] **`PipelineRunner` (The Conductor)**: Implemented `src/app/use_cases/pipeline_runner.py` as the singular long-lived orchestrator. It is responsible for resolving handles via `StreamManager`, creating the `PipelineBlueprint`, and managing the engine lifecycle.
- [x] **`PipelineBuilder` (Fluent Proxy)**: Refactored `src/app/use_cases/pipeline_builder.py` to follow the **Builder-as-a-Proxy** pattern. It now acts as a transient DSL that performs "Contract Adjudication" (type safety checks) and then hands over the intent to the `PipelineRunner` without resolving handles prematurely.

---

## 3. Immediate Next Steps (Pending Implementation)

The orchestration layer is fully set up. The next tasks revolve around infrastructure and wiring:

1.  **Local Engine Adapter**: Implement `src/infrastructure/engines/local_engine.py` using a sequential pull-loop for fan-in and broadcast for fan-out. It must conform to the `PipelineEngine` output port contract.
2.  **Bootstrap Wiring**: Update `src/app/bootstrap.py` to:
    - Initialize the `EngineRegistry` and register the `LocalEngine`.
    - Construct the `PipelineRunner`.
    - Assemble and return the newly refined `AppContext` (instead of just `StreamManager`).
3.  **StreamClient Finalization**: Update `src/app/stream_client.py` to accept the `AppContext` and fully integrate the `.pipeline()` method. The method should instantiate a fresh `PipelineBuilder` linked to the `AppContext.pipeline_runner` for each call.

---

## 4. Architectural Instructions for the Next Instance

- **Hexagonal Integrity**: Maintain the separation established by the "Builder-as-a-Proxy" pattern. The `PipelineBuilder` strictly handles intent collection and type validation (Domain Rules), while the `PipelineRunner` handles physical resource resolution and execution orchestration (Application Logic).
- **The "Generator Pitfall"**: When implementing the `LocalEngine`, avoid deep nesting. Use the engine to flatten the data flow logic while iterating over the `PipelineBlueprint` sources and sinks.
- **Error Translation**: All engines *must* catch lower-level OS/Network exceptions and re-raise them as `PipelineExecutionError`.
- **Resource Lifecycle**: Always use the `with engine.setup(blueprint)` pattern to ensure the engine's `shutdown()` method is called by the Python runtime.
- **Traceability**: Ensure the `trace_id` is passed correctly from the `PipelineBuilder` -> `PipelineRunner` -> `StreamManager` (when getting handles) & `PipelineEngine` (when instantiating) to maintain end-to-end observability.

---

## 5. Key Reference Files

- `docs/implementation/pipeline_subsystem_blueprint.md`: The master design document.
- `src/app/use_cases/pipeline_runner.py`: The application orchestrator.
- `src/app/use_cases/pipeline_builder.py`: The fluent proxy UI.
- `src/app/ports/output/pipeline_engine.py`: The engine contract.
- `src/app/domain/models/pipeline/blueprint.py`: The job definition.
