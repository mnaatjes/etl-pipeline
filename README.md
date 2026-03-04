## Design Philosophy

StreamFlow is built on the principles of **Clean Architecture** and **Domain-Driven Design (DDD)**. Key architectural decisions include:

- **Hexagonal Architecture (Ports & Adapters):** Core logic is completely decoupled from infrastructure (filesystems, APIs). This allows for protocol-agnostic stream operations.
- **High-Resolution Identity:** The framework doesn't treat resources as strings. It resolves them into **Smart Value Objects** that carry both physical coordinates and security metadata.
- **Resource Boundaries:** Security is a first-class citizen. Every protocol must register a `Boundary` that acts as a domain-level firewall, preventing path traversal and unauthorized resource access.
- **Composition Root:** Dependency injection is centralized in the `Bootstrap` layer, ensuring that all components are correctly wired and that the system remains 100% testable without reliance on complex mocking.
- **The Waterfall Engine:** Configuration follows a strict priority hierarchy (Global -> Local Overrides), ensuring consistent defaults while allowing for granular runtime control.

## Directory Structure

```text
src/
├── app/                        # The Composition Root & Facade
│   ├── domain/                 # Core Domain Models & Services
│   │   ├── models/             # Value Objects (Envelope, AppConfig, Identity)
│   │   └── services/           # Logic (Catalog, Factory, Resolver)
│   ├── ports/                  # Interfaces (Input/Output Boundaries)
│   ├── registry/               # Adapter Blueprints
│   ├── use_cases/              # Orchestration (StreamManager)
│   ├── bootstrap.py            # Dependency Injection & Wiring
│   └── stream_client.py        # Public Facade
└── infrastructure/             # Concrete Implementations
    └── adapters/               # Protocol Adapters
        ├── posix_file/         # Local File System (POSIX)
        └── http/               # External Web Resources (HTTP)
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

# 2. Check if a resource exists
if client.exists("registry://data/input.txt"):
    # 3. Read content (returns an iterator of Envelopes)
    stream_data = client.read("registry://data/input.txt")
    for envelope in stream_data:
        print(envelope.payload)

# 4. Write content
client.write("registry://logs/app.log", "Operation successful")
```

## Core Methods

### `get_stream(uri, as_sink=False, **overrides)`
Returns a `DataStream` instance for fine-grained control.
```python
with client.get_stream("registry://data/input.txt", chunk_size=2048) as stream:
    for envelope in stream.read():
        process(envelope.payload)
```

### `read(uri)`
Convenience method to read all content from a URI. Returns an iterator of `Envelope` objects.

### `write(uri, data)`
Convenience method to write data to a URI. Automatically wraps data in a domain `Envelope`.

### `exists(uri)`
Checks if a resource exists at the given URI without opening a stream.

## Configuration & Properties

### Global Settings (Tier 1)
Pass a dictionary to the `StreamClient` constructor to override global defaults.
- `env`: `DEV`, `PROD`, `TEST`
- `log_level`: `INFO`, `NONE`
- `chunk_size`: Default buffer size (integer)
- `enable_telemetry`: Boolean

```python
client = StreamClient(config={"chunk_size": 4096, "env": "PROD"})
```

### Stream-Specific Overrides (Tier 3)
Pass keyword arguments to `get_stream`, `read`, or `write` to override settings for a specific operation.
- `file_mode`: e.g., `"rb"`, `"wb"`, `"a"`
- `encoding`: e.g., `"utf-8"`, `"ascii"`
- `permissions`: Octal file permissions (e.g., `0o644`)

## Supported Adapters

| Protocol | Adapter | Description |
| :--- | :--- | :--- |
| `posix` | `PosixFileStream` | Local Linux/POSIX file system access with boundary security. |
| `http` | `HttpStream` | (Planned) External HTTP/HTTPS resource access. |

## URI Schemes
- **Internal (`registry://[key]/path`)**: Resolved via the `ResourceCatalog` using pre-configured anchors.
- **External (`[protocol]://[path]`)**: Direct access using standard protocols (e.g., `https://example.com/data.json`).
