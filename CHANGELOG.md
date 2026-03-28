# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- **Discovery API (Gateway)**: Implemented a suite of high-level utility methods for framework inspection:
    - `get_resources()`: Returns a structured snapshot of all registered resource anchors and their security boundaries.
    - `get_resource(key)`: Retrieves granular metadata for a single logical registration.
    - `get_protocols()`: Lists all technical protocols (drivers) currently supported by the framework.
    - `resolve(uri)`: Translates logical URIs into their physical, secured Coordinates for debugging and traceability.
    - `has_resource(key)`: Verifies if a specific logical anchor is registered.
    - `is_supported_uri(uri)`: Performs a "dry run" to check if the system can handle a specific address.
    - `is_supported_protocol(p)`: Confirms if a technical driver is loaded.
    - `get_registered_adapter(p)`: Identifies the adapter implementation class for a given protocol.
- **Middleware Subsystem (Localized Engine)**: Fully refactored transformations into a decoupled, stream-isolated model:
    - `MiddlewareCatalog`: A localized registry for a specific stream's processors.
    - `MiddlewareEngine`: An execution engine using depth-first recursion and functional chaining (`intercept`).
    - `StreamHandle`: Now serves as the definitive **Composition Root**, orchestrating the handoff between Adapters and the Middleware Engine.
- **Identity Subsystem**: Added `register_resource()` to the `ResourceManager` as a unified, high-level configuration entry point for physical anchors.

### Changed
- **Architectural Purity**: Successfully stripped all transformation logic from the `DataStream` port and infrastructure adapters (`PosixFileStream`, `HttpStream`).
- **Symmetric Delegation**: Established a consistent cross-layer pattern (Gateway -> StreamManager -> ResourceManager) for all discovery and configuration operations.
- **Documentation**: Enhanced all primary facades and models with verbose, example-rich docstrings.

### Fixed
- **Identity Inconsistency**: Fixed a bug in Network resource registration where the protocol was not correctly propagated to the Coordinate.
- **Leaky Middleware Abstractions**: Resolved the SRP violation where the `DataStream` port was responsible for transformation orchestration.

## [0.9.1]
### Added
- **Documentation**: Updated `docs/examples/` documentation.
- **Agents and Scripts**: Added local `.agents/` and `.scripts/` directories to manage development.

## [0.9.0]
### Added
- **Slalom Branding Refactor**: Successfully transitioned the project to the "Slalom" brand, establishing a high-fidelity "Stream Orchestration Framework" identity.
- **Gateway Entry Point**: Implemented the `Gateway` class as the primary Smart Gateway, abstracting complex IoC orchestration into a simple, professional API.
- **SessionManager Facade**: Implemented a dedicated manager for the Session Context subsystem, handling Traceability (Passports) and the Settings "Waterfall."
- **ResourceManager Facade**: Implemented a single entry point for the identity subsystem to manage the full lifecycle: *Classify -> Resolve -> Map -> Validate*.
- **Master Architecture Index**: Created a high-signal `docs/architecture/README.md` featuring the "3-Diagram Rule" (Structural Map, Golden Path Sequence, and Entity Genealogy).
- **Specialized Provider Hierarchy**: Refactored the composition root into layered providers (`Config`, `Session`, `Identity`, `Stream`, `Pipeline`) for zero-redundancy dependency injection.
- **Visual Test Suite**: Implemented unit tests for `SessionManager` using manual fakes and `rich.inspect` for real-time terminal tracing of object state.
- **SessionContext:** Added `spawn()` method to merge `overrides` Dict property through system.

### Changed
- **Architectural Naming Standard**: Renamed all "Orchestrator" facades to "Managers" (`ResourceManager`, `SessionManager`) to clarify their roles as subsystem caretakers.
- **Documentation Consolidation**: Reorganized the `docs/` directory into conventional hierarchies, removing redundant "as-built" and "implementation" folders.
- **StreamManager Refinement**: Fully refactored the `StreamManager` use-case to delegate "What" (Identity/Policy) to the `ResourceManager` and "How" (Settings/Context) to the `SessionManager`.
- **Identity Registration:** Removed `ProtocolRegistration` dataclass and replaced with `AdapterBlueprint`.
- Ret-conned versioning strategy to reflect the pre-Slalom experimental phase as `0.x.x`.
- Consolidation of the identity refactor and session context work into the final alpha milestone.

### Fixed
- **SessionContext:** Now carries `overrides` through system from `Gateway()` to call_level methods.
- **Adapters**: Refactored to accept ResourceIdentity types.
- **Registration Holes**: Closed the configuration gaps in `StreamManager.add_resource()` and implemented the delegation logic in `ResourceManager`.
- **Lifecycle Management**: Implemented a robust `teardown` sequence in the `Bootstrap` class for graceful resource release.

## [0.3.0] - 2026-03-04
### Added
- **Smart Gateway Pattern**: Evolved the framework from a proxy to an intelligent resource mediator.
- **Self-Aware Packets**: Replaced the legacy `Envelope` system with a high-resolution `Packet` model.
- **Unified StreamContext**: Implemented a "Passport" system for data, ensuring every byte is stamped with a `trace_id`.

## [0.2.0] - 2026-03-04
### Added
- **Catalog-Aware Resolution**: Initial implementation of intelligent URI resolution.
- **Protocol Safelist**: Added a security firewall to prevent unrecognized URI schemes.

## [0.1.0] - 2026-03-03
### Added
- Initial release of the Slalom prototype.
- Basic support for POSIX and HTTP adapters.
- Composition Root (Bootstrap) architecture.
