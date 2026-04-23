---
id: ADR-002
title: "Adopt Outside-In Implementation Sequence"
status: proposed
created_at: 2026-04-23
updated_at: 2026-04-23
component: core
type: "explanation/adr"
epic_link: "https://github.com/mnaatjes/etl-pipeline/issues/14"
---

# Context

The Slalom Rebirth (ADR-001) established the goal of a lean ETL core. To avoid the over-engineering and "Inside-Out" drift that plagued v0.9.0, we require a disciplined implementation sequence that prioritizes the consumer's interface and internal contracts before building physical infrastructure.

# Decision

We will adopt an **Outside-In Design** strategy, specifically following the sequence defined in `.slalom/roadmap.yml`. This ensures that every line of internal code is justified by a direct requirement of the public Gateway API.

### Professional Patterns Applied:

1. **Outside-In Design:** Starting at the Gateway (the API) and working inward to the Domain and Infrastructure. This prevents "Gold-Plating" and ensures the library is ergonomic.
2. **README-Driven Development (RDD):** The "Dream API" defined in our strategy serves as the primary requirement. All internal components are built to fulfill the `app.pipeline(...).through(...).to(...).run()` syntax.
3. **Consumer-Driven Contracts:** The `Packet` and `MiddlewareProcessor` interfaces are defined by what the `PipelineBuilder` needs to pass between steps, not by what the adapters are capable of.
4. **Interface-Driven Development:** Defining Abstract Base Classes (Ports) for `DataStream` and `MiddlewareProcessor` before writing any concrete implementation (Adapters/Processors).

# Implementation Sequence (The Roadmap)

1. **The Unit of Work (Packet):** Define the smart immutable container for data.
2. **The Filter Contract (Middleware Port):** Define the transformation interface.
3. **The Pipe Contract (DataStream Port):** Define the I/O interface.
4. **The Architect (PipelineBuilder):** Implement the fluent DSL state-collector.
5. **The Resolver (fsspec):** Implement the functional protocol-agnostic mapping.
6. **The Front Door (Slalom Gateway):** Implement the polished library entry point.

# Consequences

### Positive
- **Ergonomic API:** Ensures the framework is intuitive and easy to use from day one.
- **Minimalist Core:** No "Ghost Code" or unused internal abstractions.
- **Test-First Readiness:** Contracts and Interfaces are defined early, making the system easy to mock.

### Negative
- **Delayed Physical I/O:** We will have a working "Builder" and "Engine" before we have a real "File Writer," as we prioritize the contract over the side-effect.
- **Abstract Complexity:** Requires high mental discipline to keep Domain logic oblivious to Infrastructure during the early steps.
