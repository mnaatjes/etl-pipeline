---
id: ADR-001
title: "Pivot to Lean Streaming Architecture (Slalom Rebirth)"
status: proposed
created_at: 2026-04-23
updated_at: 2026-04-23
component: core
type: "explanation/adr"
epic_link: PENDING
---

# Context

The current Slalom framework has evolved into a "Framework for the sake of a Framework," where the complexity of resource identification and session management significantly outweighs the functional utility of streaming ETL. Structural interrogation reveals that approximately 60% of the domain layer is dedicated to an over-engineered identity resolution subsystem (Realms, Addresses, Coordinates) that has never been used for its intended purpose.

The current system suffers from:
1. **High Cognitive Load:** A quadruple-layered delegation chain (Gateway -> StreamManager -> ResourceManager -> SessionManager).
2. **Dead Code Bloat:** Multiple unused identity realms and placeholder modules.
3. **Pre-emptive Generalization:** Architectural rigidity that prevents rapid development of the core mission: reliable source-to-sink streaming.

# Decision

We will "Rebirth" the system by stripping away the bureaucratic layers and identity framework, focusing exclusively on a high-performance, functional ETL core. 

### Key Transitions:
- **Flattened Orchestration:** Replace the multi-manager hierarchy with a single functional orchestrator and a simplified entry point.
- **Contract Modernization:** Move from manual `StreamContract` type-guarding to standard Python library or Pydantic-based validation.
- **Native Identity:** Replace the custom 11-file identity subsystem with standard library URI and Path parsing.
- **Session Collapse:** Reduce the `SessionContext` service hierarchy to a simple, traceable settings dictionary.

# Retained Components (The Functional Core)

The following high-value entities and logic will be salvaged and migrated to the new architecture:

1. **The "Smart Unit of Work" (Packet Models):**
   - `Packet` Model (`src/app/domain/models/packet/base.py`): Immutable dataclass with lineage-aware `spawn()`.
   - `FlowSignal` & `Completeness` (`src/app/domain/models/packet/flow.py`): For end-of-stream (Flush) signals.
   - `PayloadSubject` (`src/app/domain/models/packet/payload.py`): Shared vocabulary (BYTES, JSON, DICT).

2. **The Functional Chaining (Middleware Engine):**
   - `MiddlewareEngine` (`src/app/domain/models/middleware/engine.py`): Recursive transformation logic and iterator interception.
   - Flush Mechanism: Ensuring stateful processors (aggregators) clear buffers.

3. **Physical Streaming I/O:**
   - `HttpStream` Adapter (`src/infrastructure/adapters/http/adapter.py`): `httpx`-based streaming strategies.
   - `PosixFileStream` Adapter (`src/infrastructure/adapters/posix_file/adapter.py`): Core I/O loop and directory management.
   - `DataStream` Port (`src/app/ports/output/datastream.py`): Standard I/O contract.

4. **High-Performance Processors:**
   - `JsonStreamProcessor` (Streaming ijson parser).
   - `GzipDecompressor` (Streaming zlib decompression).
   - `ChecksumProcessor` (Pass-through hash calculation).

5. **Developer Experience:**
   - `PipelineBuilder` (`src/app/use_cases/pipeline_builder.py`): Fluent DSL syntax and contract adjudication.

6. **Context Passport:**
   - `StreamContext` (`src/app/domain/models/streams/stream_context.py`): Lightweight origin and trace tracking.

# Discarded Components (The "Mess")

- `src/app/domain/models/resource_identity/**`: Entire subsystem removed in favor of standard URI parsing.
- `src/app/domain/services/session_context/**`: Hierarchy collapsed.
- `src/app/providers/**`: Two-phase bootloading removed.
- `src/app/gateway.py` & `src/app/container.py`: Bureaucratic layers removed.

# Consequences

### Positive
- **Reduced Cognitive Complexity:** Developers can understand the path from `read()` to `write()` without navigating four managers.
- **Improved Performance:** Lower overhead per packet by eliminating redundant transformation/validation layers.
- **Easier Maintenance:** Smaller codebase focused on the core ETL mission.

### Negative
- **Breaking Change:** This represents a full system rebirth; existing client code using the `Gateway` or `ResourceManager` will require migration.
- **Manual Migration:** Existing adapters and processors must be surgically moved to the new structure.
