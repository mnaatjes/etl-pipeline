# Slalom Framework

![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)

## Directory Structure

```text
src/
└── slalom/
    ├── __init__.py          # Public API Exposure & Version
    ├── gateway.py           # [Step 6] The "Front Door" (Slalom class)
    │
    ├── core/                # THE DOMAIN (Pure Logic, Zero Infrastructure deps)
    │   ├── packet.py        # [Step 1] Smart Unit of Work & PayloadSubject
    │   ├── engine.py        # [Step 1.1] Recursive Middleware Engine
    │   └── builder.py       # [Step 4] PipelineBuilder (Fluent DSL State)
    │
    ├── ports/               # THE CONTRACTS (Interfaces/ABCs)
    │   ├── middleware.py    # [Step 2] MiddlewareProcessor Port
    │   └── datastream.py    # [Step 3] DataStream Port
    │
    └── infrastructure/      # THE ADAPTERS (External side-effects)
        ├── resolver.py      # [Step 5] fsspec-based Unified Resolver
        └── adapters/        # Physical I/O implementations
            ├── file.py      # PosixFileStream
            └── http.py      # HttpStream
```

## Getting Started

### Installation


### Basic Usage
The `Gateway` is the primary entry point for all operations.

## Core Methods

---

## Documentation Architecture

The Slalom project maintains a structured documentation suite organized by **Permanence** and **Intent**.
