# Middleware & Pipeline Architecture (Refactor 2026)

This document defines the core architectural decisions for the transition from the legacy `Envelope` system to the modern `Packet-Processor` framework within the StreamFlow library.

## 1. Core Philosophy
The architecture follows a **Hexagonal (Ports & Adapters)** pattern combined with a **Pipe and Filter** stream processing model. The goal is to create a transport-agnostic, low-friction environment for high-volume data transformation (200GB+) under strict resource constraints (30GB disk).

## 2. The Smart Unit of Work: `Packet`
The `Packet` (formerly `Envelope`) is the primary data carrier. Unlike a passive container, it is a **lifecycle-aware message** that coordinates the flow of the pipeline.

### Foundational Components
| Component | Responsibility | Domain Entity |
| :--- | :--- | :--- |
| **The "When"** | Stream lifecycle and buffering signals. | `FlowSignal` |
| **The "What"** | Descriptive label for payload state/schema. | `PayloadType` |
| **The "Who"** | Traceability and parent-child lineage. | `Identity` |
| **The "Where/Why"** | Structured metadata and origin tracking. | `PipelineContext` |

### Flow Signals
- `ATOMIC`: A single, complete unit. No buffering required.
- `STREAM_START`: The first packet; triggers engine/buffer initialization.
- `STREAM_DATA`: Intermediate chunk; triggers accumulation/processing.
- `STREAM_END`: The "Flush" signal; triggers buffer emptying and finalization.

## 3. The Unified Middleware Contract
We have collapsed complex sub-ports (Byte vs. Object) into a single, polymorphic **`MiddlewareProcessor`**.

### Key Responsibilities
1. **`process(Packet) -> Iterator[Packet]`**: The core transformation logic.
2. **`flush() -> Iterator[Packet]`**: Triggered by `STREAM_END` to drain internal buffers.
3. **`open() / close()`**: Resource management (Context Manager pattern) for internal engines (e.g., DuckDB).

### Functional Modes
- **Stateless (1:1)**: Receives one packet, yields one packet.
- **Exploding (1:N)**: Normalization logic (e.g., unnesting arrays). Uses `Identity.spawn()` to maintain correlation.
- **Aggregating (N:1)**: Buffering logic. Collects `STREAM_DATA` and yields a single packet upon `STREAM_END`.

## 4. Directory Structure (Hexagonal)
To maintain separation of concerns, the entities are placed as follows:

```text
src/app/domain/models/
├── flow.py           # FlowSignal (Enum)
├── context.py        # PipelineContext (Data Bag)
├── identity.py       # Identity (Lineage)
├── payload.py        # PayloadType (Labels)
└── packet.py         # The Unified Packet Entity

src/app/ports/output/
└── processor.py      # The MiddlewareProcessor Interface (Port)

src/infrastructure/
└── processors/       # Concrete Implementations (Adapters)
    ├── duckdb/       # Normalization Engine
    └── validation/   # Data Quality Filters
```

## 5. Implementation Strategies
- **Dynamic Handshaking**: Use `PayloadType` string labels for low-friction connections between middleware without a central registry.
- **Immutability**: The `PipelineContext` and `Identity` objects should be immutable, using "Spawn" or "With" patterns to create derivatives.
- **Graceful Evolution**: The `Packet` is introduced as a superior successor to `Envelope`, maintaining backwards compatibility where necessary during the refactor.
