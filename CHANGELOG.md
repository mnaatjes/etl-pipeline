# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2026-03-19
### Added
- **SessionManager Facade**: Implemented a dedicated manager for the Session Context subsystem, handling Traceability (Passports) and the Settings "Waterfall."
- **ResourceManager Facade**: Implemented a single entry point for the identity subsystem to manage the full lifecycle: *Classify -> Resolve -> Map -> Validate*.
- **Refined ResourceBoundary Ports**: Created realm-specific input ports (`LocalResourceBoundary`, `NetworkResourceBoundary`, etc.) using the **Template Method** pattern for centralized security enforcement.
- **HttpResourceBoundary**: Dedicated adapter for URL security, implementing host-locking and protocol consistency.
- **Master Architecture Index**: Created a high-signal `docs/architecture/README.md` featuring the "3-Diagram Rule" (Structural Map, Golden Path Sequence, and Entity Genealogy).
- **SessionContext Example Guide**: Added `docs/examples/session_context.md` to provide a clear developer "Quick Start" for traceability and overrides.
- **Visual Test Suite**: Implemented unit tests for `SessionManager` using manual fakes and `rich.inspect` for real-time terminal tracing of object state.
- **Unified Service Exports**: Clean entry point for identity and session services in their respective `__init__.py` files.

### Changed
- **Architectural Naming Standard**: Renamed all "Orchestrator" facades to "Managers" (`ResourceManager`, `SessionManager`) to clarify their roles as subsystem librarians and caretakers.
- **Documentation Consolidation**: Reorganized the `docs/` directory into conventional `architecture/`, `design/`, `examples/`, and `status_reports/` hierarchies, removing redundant "as-built" and "implementation" folders.
- **StreamManager Refinement**: Fully refactored the `StreamManager` use-case to delegate "What" (Identity/Policy) to the `ResourceManager` and "How" (Settings/Context) to the `SessionManager`.
- **Settings Waterfall Resolution**: Centralized the ephemeral settings merging logic into the `SessionManager` via the `SettingsResolver`.
- **Registry-Driven Classification**: Refactored `ResourceFactory` to dynamically discover resource realms via the `StreamRegistry`, eliminating hardcoded protocol lists.
- **Protocol-Agnostic Catalog**: Updated `ResourceCatalog` to take precedence based on resource nicknames (keys), regardless of the URI protocol used.
- **DataStream Migration**: Updated the `DataStream` output port to strictly consume the new `Coordinate` model instead of legacy `StreamLocation`.

### Fixed
- **Absolute Path Injection**: Fixed a vulnerability in `LocalResourceBoundary` where absolute paths could be injected as sub-paths.
- **Host Redirection Hijacking**: Implemented "Authority Locking" in `NetworkResourceBoundary` to prevent unauthorized host redirection.
- **Redundant URL Segments**: Fixed a logic error in URL joining that caused duplicated path segments (e.g., `v1/v1/`).
- **Memory Constructor Mismatches**: Fixed argument errors in `Memory`, `Synthetic`, and `Virtual` coordinate constructors.

### Removed
- **Legacy Identity Terminology**: Purged all remaining references to `ResourceOrchestrator`, `ContextOrchestrator`, `StreamLocation`, and `PhysicalPath` from code and documentation.
- **Hardcoded Protocols**: Removed static protocol-to-realm mappings from the domain services.

## [## [Unreleased]] - 2026-03-04
### Added
- **Smart Gateway Pattern**: Evolved the framework from a proxy to an intelligent resource mediator.
- **Self-Aware Packets**: Replaced the legacy `Envelope` system with a high-resolution `Packet` model.
...
