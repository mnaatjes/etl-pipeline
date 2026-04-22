# Component Model and Hierarchy

This document maps the architectural hierarchy of the pipeline engine, detailing the responsibilities and relationships between core components.

## Architecture Hierarchy

| Part | Zone (Directory) | Responsibility | Core Properties | Primary Methods | Relationship |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **AppConfig** | `src/app/ports/` | The Regime: Holds static system-wide constants. | env, log_level, default_chunk_size | N/A (Dataclass) | Fed into the Resolver and Bootstrapper. |
| **StreamContract** | `src/app/ports/` | The Blueprint: Abstract template for all stream settings. | chunk_size, use_lines | N/A (Abstract) | Inherited by specific settings (e.g., HttpSettings). |
| **SettingsResolver** | `src/app/ports/` | The Logic Tool: Calculates the 3-tier Waterfall merge. | app_config, protocol_overrides | `resolve(protocol, overrides)` | Used as a "brain" by the StreamManager. |
| **StreamRegistry** | `src/infrastructure/` | The Catalog: Maps URIs to physical Stream Adapters. | _protocols (internal map) | `get_stream(uri, **kwargs)` | Infrastructure "Library" used by the StreamManager. |
| **StreamManager** | `src/app/` | The Dispatcher: The long-lived face of the package. | registry, resolver | `get_stream(uri, **overrides)` | Combines Resolver logic with Registry data. |
| **Bootstrapper** | `src/app/` | The Assembler: Short-lived setup script. | app_config, protocol_overrides | `build_manager()` | The "Birth Event" that produces the StreamManager. |

## The Relational Flow (Step-by-Step)

### 1. Bootstrap Phase (Initialization)
- User creates a `Bootstrapper` with an `AppConfig`.
- User adds protocol-specific `StreamContract` implementations (e.g., `HttpSettings`).
- `Bootstrapper` instantiates the `StreamRegistry` and the `SettingsResolver`.

### 2. Management Phase (Transition)
- `Bootstrapper` hands the `Registry` and `Resolver` over to the `StreamManager`.
- `Bootstrapper` instance is discarded.
- `StreamManager` becomes the long-lived "Source of Truth."

### 3. Execution Phase (Call-Time)
- User calls `manager.get_stream(uri, **overrides)`.
- `StreamManager` asks `Resolver` to calculate final properties (Waterfall Tier 1 + 2 + 3).
- `StreamManager` passes final properties to the `Registry`.
- `Registry` returns a concrete `DataStream` (Local or HTTP).

## Summary of Zones
- **`src/app/ports/` (The Definitions):** The "Rules." Pure data and abstract contracts.
- **`src/app/` (The Orchestration):** The "Logic." Bootstrap and Management live here.
- **`src/infrastructure/` (The Mechanics):** The "Gears." Registry and physical Stream Adapters live here.
