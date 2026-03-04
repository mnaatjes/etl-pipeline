# StreamFlow Framework

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)

## Design Philosophy

StreamFlow is built on the principles of **Clean Architecture**, **Domain-Driven Design (DDD)**, and the **Smart Gateway** pattern. Key architectural decisions include:

- **Hexagonal Architecture (Ports & Adapters):** Core logic is completely decoupled from infrastructure (filesystems, APIs). This allows for protocol-agnostic stream operations.
- **Smart Gateway Pattern:** The framework acts as an intelligent mediator. It doesn't just pass bytes; it negotiates **Capabilities**, injects **Context**, and enforces **Security Boundaries**.
- **High-Resolution Identity:** Resources are resolved into **Smart Value Objects** that carry physical coordinates, lineage, and security metadata.
- **Context-Aware Observability:** Every data unit (**Packet**) is stamped with a **StreamContext** (Passport) containing a unique `trace_id`, enabling end-to-end observability.
- **Composition Root:** Dependency injection is centralized in the `Bootstrap` layer, ensuring the system is 100% testable without complex mocking.

## Directory Structure

```text
src/
├── app/                        # The Composition Root & Facade
│   ├── domain/                 # Core Domain Models & Services
│   │   ├── models/             
│   │   │   ├── packet/         # The Self-Aware Unit of Work (Packet, FlowSignal)
│   │   │   ├── streams/        # Smart Resource Models (Handle, Capacity, Context)
│   │   │   └── resource_identity/ # Identity Objects (LogicalURI, PhysicalPath)
│   │   └── services/           # Logic (Catalog, Factory, Resolver)
│   ├── ports/                  # Interfaces (Input/Output Boundaries)
│   ├── registry/               # Adapter Blueprints
│   ├── use_cases/              # Orchestration (StreamManager)
│   ├── bootstrap.py            # Dependency Injection & Wiring
│   └── stream_client.py        # Public Facade
└── infrastructure/             # Concrete Implementations
    └── adapters/               # Protocol Adapters (POSIX, HTTP)
```

## Getting Started

### Installation
Ensure `src/` is in your `PYTHONPATH`.

### Basic Usage
The `StreamClient` is the primary entry point for all operations.

```python
from src.app import StreamClient

# 1. Initialize the client
client = StreamClient()

# 2. Request a Smart Handle (The dashboard for your resource)
handle = client.get_handle("posix://data/input.txt", read_mode="lines")

# 3. Use Introspection (Ask what is possible)
if handle.capacity.can_seek:
    print("This stream supports random access!")

# 4. Read Self-Aware Packets
with handle as stream:
    for packet in stream.read():
        print(f"[{packet.context.trace_id}] Payload: {packet.payload}")

# 5. Write content
client.write("posix://logs/app.log", b"Operation successful")
```

## Core Methods

### `get_handle(uri, as_sink=False, **overrides)`
Returns a `StreamHandle` instance. This is the **Smart Gateway** entry point.
- Provides access to `capacity` (introspection).
- Manages stream lifecycle via context manager.
- Yields traceable `Packet` objects.

### `read(uri)`
Convenience method to read all content from a URI. Returns an iterator of `Packet` objects.

### `write(uri, data)`
Convenience method to write data to a URI. Automatically wraps data in a traceable `Packet`.

### `exists(uri)`
Checks if a resource exists at the given URI without opening a stream.

### `resolve(uri)`
Exposes the internal resolution logic, returning the physical `Path` or `URL`.

## Resource Access Modes

### 1. Catalog-Aware Access (`posix://`, `s3://`, etc.)
The framework is **Polite**. If you register a key in the catalog, you can access it using its protocol scheme directly.

**Registration:**
```python
client.add_resource(key="vault", protocol="posix", anchor="/var/lib/data")
```

**Intuitive Usage:**
```python
# Automatically resolves to /var/lib/data/reports/2026.csv
client.read("posix://vault/reports/2026.csv")
```

### 2. Mandatory Identity (`registry://`)
Standard internal resolution. Always safe, always governed by boundaries.
```python
client.read("registry://vault/config.json")
```

### 3. Direct Access (`file://`, `https://`)
Direct physical access bypassing the catalog. Subject to the **Protocol Safelist** firewall.

---

## Observability & Introspection

### StreamContext (The Passport)
Every stream generates a unique `trace_id`. Every `Packet` produced by that stream carries this context, allowing you to trace a single piece of data through multiple middleware processors.

### StreamCapacity (The Dashboard)
Adapters declare their capabilities upfront:
- `can_seek`: Can the stream move to an offset?
- `is_writable`: Does the resource support writing?
- `is_network`: Is this a remote resource?

## Supported Adapters

| Protocol | Adapter | Capabilities |
| :--- | :--- | :--- |
| `posix` / `file` | `PosixFileStream` | Seekable, Writable, Local |
| `http` / `https` | `HttpStream` | Sequential, Read-Only, Network |
