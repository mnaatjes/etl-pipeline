---
id: ADR-001
title: "Pivot to Lean Streaming Architecture (Slalom Rebirth)"
status: proposed
created_at: 2026-04-23
updated_at: 2026-04-23
component: core
type: "explanation/adr"
epic_link: "https://github.com/mnaatjes/etl-pipeline/issues/13"
---

# Context

The current Slalom framework has evolved into a "Framework for the sake of a Framework," where the complexity of resource identification and session management significantly outweighs the functional utility of streaming ETL. Structural interrogation reveals that approximately 60% of the domain layer is dedicated to an over-engineered identity resolution subsystem (Realms, Addresses, Coordinates) that has never been used for its intended purpose.

The current system suffers from:
1. **High Cognitive Load:** A quadruple-layered delegation chain (Gateway -> StreamManager -> ResourceManager -> SessionManager).
2. **Dead Code Bloat:** Multiple unused identity realms and placeholder modules.
3. **Pre-emptive Generalization:** Architectural rigidity that prevents rapid development of the core mission: reliable source-to-sink streaming.

# Decision

We will "Rebirth" the system by stripping away the bureaucratic layers and identity framework, building a high-performance, functional ETL core from the ground up. All previous v0.9.0 code has been removed; this is a greenfield implementation.

### Key Transitions:
- **Flattened Orchestration:** A single functional orchestrator and a simplified entry point.
- **Contract Modernization:** Native Pydantic-based validation.
- **Standard Library Identity:** Utilization of standard URI and Path parsing.
- **Session Simplicity:** A simple, traceable settings dictionary.

# Target Functional Core (Re-implementation Requirements)

The following high-value patterns and functional requirements from previous iterations will be built fresh in the new architecture:

1. **The "Smart Unit of Work" (Packet Models):**
   - Immutable `Packet` Model with parent-child correlation tracking (`spawn()`).
   - `FlowSignal` & `Completeness` for stream lifecycle (Start, Data, End/Flush).
   - `PayloadSubject` shared vocabulary (BYTES, JSON, DICT).

2. **The Functional Chaining (Middleware Engine):**
   - A generator-based transformation engine using recursive logic.
   - Mandated flush mechanism for stateful processors (aggregators).

3. **Physical Streaming I/O:**
   - Standardized `DataStream` Port for all I/O.
   - `HttpStream` and `PosixFileStream` implementations using professional streaming libraries.

4. **Essential Processors:**
   - Streaming JSON parsing (Regime Changer).
   - Streaming GZIP decompression.
   - Real-time checksum/hash calculation.

5. **Developer Experience:**
   - A Fluent DSL (PipelineBuilder) for building type-safe transformation chains.

# Discarded Concepts (Non-Goals)

- **Custom Identity Modeling:** No manual tracking of Addresses or Coordinates.
- **Manager-Facade Chains:** No quadruple-layered delegation.
- **Two-Phase Bootloading:** No complex IoC provider hierarchy.

# Consequences

### Positive
- **Drastic Complexity Reduction:** Zero technical debt carryover.
- **Improved Performance:** Minimal overhead between raw I/O and user logic.
- **Standardization:** Heavy reliance on industry-standard libraries (`fsspec`, `pydantic`).

### Negative
- **Full Re-implementation:** All core logic must be written fresh to ensure alignment with new standards.
- **Breaking API:** Complete lack of backward compatibility with legacy Slalom scripts.
