# Slalom Framework

![Version](https://img.shields.io/badge/version-0.9.0-blue.svg)

## Design Philosophy

**Slalom** is a high-fidelity **Stream Orchestration Framework** built on the principles of **Clean Architecture**, **Domain-Driven Design (DDD)**, and the **Smart Gateway** pattern. 

Key architectural decisions include:

- **Hexagonal Architecture (Ports & Adapters):** Core logic is completely decoupled from infrastructure. This allows for protocol-agnostic stream operations.
- **Smart Gateway Pattern:** The framework acts as an intelligent mediator. It doesn't just pass bytes; it negotiates **Capabilities**, injects **Context**, and enforces **Security Boundaries**.
- **High-Resolution Identity:** Resources are resolved into **Smart Value Objects** (Coordinates) that carry physical coordinates, lineage, and security metadata.
- **Context-Aware Observability:** Every data unit (**Packet**) is stamped with a **SessionContext** (Passport) containing a unique `trace_id`, enabling end-to-end observability.
- **Composition Root:** Dependency injection is centralized in specialized **Providers**, ensuring the system is 100% testable and modular.

## Directory Structure

```text
src/
├── app/                        # The Composition Root & Facade
│   ├── domain/                 # Core Domain Models & Services
│   │   ├── models/             
│   │   │   ├── packet/         # The Self-Aware Unit of Work (Packet)
│   │   │   ├── streams/        # Smart Resource Models (Handle, Capacity)
│   │   │   └── resource_identity/ # Identity Objects (Address, Coordinate)
│   │   └── services/           # Logic (ResourceManager, SessionManager)
│   ├── ports/                  # Interfaces (Input/Output Boundaries)
│   ├── providers/              # Dependency Injection Modules
│   ├── use_cases/              # Orchestration (StreamManager)
│   ├── bootstrap.py            # Composition Root (Wiring)
│   └── gateway.py              # The Smart Gateway (Entry Point)
└── infrastructure/             # Concrete Implementations (Adapters)
```

## Getting Started

### Installation
Ensure `src/` is in your `PYTHONPATH`.

### Basic Usage
The `Gateway` is the primary entry point for all operations.

```python
from src.app import Gateway

# 1. Initialize the Gateway (The Course)
slalom = Gateway()

# 2. Request a Smart Handle (The Dashboard for your resource)
handle = slalom.get_handle("posix://data/input.txt")

# 3. Use Introspection (Ask what is possible)
if handle.capacity.can_seek:
    print("This stream supports random access!")

# 4. Read Traceable Packets
with handle as stream:
    for packet in stream.read():
        # Each packet slaloms through the gateway with its Passport
        print(f"[{packet.context.trace_id}] Payload: {packet.payload}")
```

## Core Methods

### `get_handle(uri, as_sink=False, **overrides)`
Returns a `StreamHandle`. This is the **Smart Gateway** entry point for managed I/O.

### `read(uri)`
Convenience method to read all content from a URI. Returns an iterator of traceable `Packet` objects.

### `write(uri, data)`
Convenience method to write data to a URI. Automatically stamps the data with the gateway context.

### `add_resource(key, protocol, anchor)`
Registers a physical anchor (e.g., a folder or API base) in the **Resource Catalog**.

---

## Documentation Architecture

The Slalom project maintains a structured documentation suite organized by **Permanence** and **Intent**.

```text
docs/
├── architecture/           # The "Source of Truth" (System as it exists)
│   ├── standards/          # Engineering standards & patterns
│   └── README.md           # Master System Topology & Diagrams
├── design/                 # "Living" documents for active work
│   ├── plans/              # Execution roadmaps (Refactors, Features)
│   └── proposals/          # RFCs and design specifications
├── examples/               # Developer Experience (Usage & Tutorials)
│   ├── session_context.md  # How to use Traceability & Settings
│   └── stream_client.md    # Getting started with the Gateway
└── status_reports/         # Historical snapshots of project progress
```

### 1. Architecture (`docs/architecture/`)
The **internal** guide for maintainers, covering security boundaries, data models, and the "Smart Gateway" logic.

### 2. Design (`docs/design/`)
A workspace for evolution. **Proposals** are RFCs for future work, while **Plans** are active execution roadmaps.

### 3. Examples (`docs/examples/`)
The **external** developer guide. If you need to know how to implement a specific use case, start here.
