# Pipeline Project: Handoff & Status Report

**Current Date:** March 8, 2026
**Project:** StreamFlow (Pipeline Subsystem)

---

## 1. Project Context

The StreamFlow framework is built using a **Hexagonal Architecture** with **Domain-Driven Design (DDD)** principles. It provides a protocol-agnostic, context-aware data streaming engine. The current focus is implementing a high-performance, fluent **Pipeline Subsystem**.

### Core Concepts
- **Packet**: The smart unit of work carrying context and flow signals.
- **DataStream**: The output port for resource adapters (POSIX, HTTP).
- **StreamManager**: The orchestrator for individual resource resolution and handling.
- **PipelineSubsystem**: The workflow orchestrator for data-in-motion.

---

## 2. Completed Milestones

We have completed the **Research and Strategy** phase for the Pipeline subsystem and have begun the **Implementation** phase.

### Infrastructure & Domain
- [x] **`StreamCapacity` Update**: Added `is_readable` to the `StreamCapacity` dataclass to support explicit capability handshakes.
- [x] **`PipelineBlueprint` Domain Model**: Created `src/app/domain/models/pipeline/blueprint.py`. This is the "Job Ticket" that holds the source handle, sink handle, and processors. It includes self-validation logic (`__post_init__`).
- [x] **`PipelineEngine` Port (Contract)**: Created `src/app/ports/output/pipeline_engine.py`. This abstract class defines the execution strategy, lifecycle (setup/execute/shutdown), and error translation (to `PipelineExecutionError`).
- [x] **Verification**: Created comprehensive unit tests in `tests/unit/app/ports/output/test_pipeline_engine.py` using a **Manual Mock Engine** and real domain objects. All tests pass.

---

## 3. Immediate Next Steps (Pending Implementation)

The architectural blueprint is finalized (see `docs/implementation/pipeline_subsystem_blueprint.md`). The next tasks are:

1.  **Engine Registry**: Implement `src/app/registry/engines.py` to store and retrieve pluggable execution engines (Local, Multi-process).
2.  **Pipeline Builder (Fluent DSL)**: Implement `src/app/use_cases/pipeline_builder.py`. This should provide the `.through().to()` syntax.
3.  **Pipeline Runner (The Conductor)**: Implement `src/app/use_cases/pipeline_runner.py` (or `orchestrator.py`). This is the concrete logic that pulls packets through the chain and manages lifecycle events.
4.  **Local Engine Adapter**: Implement `src/infrastructure/engines/local_engine.py` using a standard generator pull-loop.
5.  **Bootstrap Wiring**: Update `src/app/bootstrap.py` to register the `LocalEngine` into the `EngineRegistry`.
6.  **StreamClient Entry Point**: Add `.pipeline()` to `src/app/stream_client.py`.

---

## 4. Architectural Instructions for the Next Instance

- **Hexagonal Integrity**: Ensure that the `PipelineRunner` and `PipelineBuilder` remain in the `app/use_cases/` layer, while concrete engines live in `infrastructure/engines/`.
- **The "Generator Pitfall"**: When implementing the `LocalEngine`, avoid deep nesting. Use the `PipelineRunner` to flatten the data flow logic.
- **Error Translation**: All engines *must* catch lower-level OS/Network exceptions and re-raise them as `PipelineExecutionError`.
- **Resource Lifecycle**: Always use the `with engine.setup(blueprint)` pattern to ensure the engine's `shutdown()` method is called by the Python runtime.
- **Traceability**: Pass the `trace_id` from the `StreamContext` to the `PipelineEngine` to maintain end-to-end observability.

---

## 5. Key Reference Files

- `docs/implementation/pipeline_subsystem_blueprint.md`: The master design document.
- `src/app/ports/output/pipeline_engine.py`: The engine contract.
- `src/app/domain/models/pipeline/blueprint.py`: The job definition.
- `tests/unit/app/ports/output/test_pipeline_engine.py`: The reference implementation (Mock) and test suite.
