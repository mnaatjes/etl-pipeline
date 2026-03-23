# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- **Slalom Branding Refactor**: Successfully transitioned the project to the "Slalom" brand, establishing a high-fidelity "Stream Orchestration Framework" identity.
- **Gateway Entry Point**: Implemented the `Gateway` class as the primary Smart Gateway, abstracting complex IoC orchestration into a simple, professional API.
- **SessionManager Facade**: Implemented a dedicated manager for the Session Context subsystem, handling Traceability (Passports) and the Settings "Waterfall."
- **ResourceManager Facade**: Implemented a single entry point for the identity subsystem to manage the full lifecycle: *Classify -> Resolve -> Map -> Validate*.
- **Master Architecture Index**: Created a high-signal `docs/architecture/README.md` featuring the "3-Diagram Rule" (Structural Map, Golden Path Sequence, and Entity Genealogy).
- **Specialized Provider Hierarchy**: Refactored the composition root into layered providers (`Config`, `Session`, `Identity`, `Stream`, `Pipeline`) for zero-redundancy dependency injection.
- **Visual Test Suite**: Implemented unit tests for `SessionManager` using manual fakes and `rich.inspect` for real-time terminal tracing of object state.
- **SessionContext:** Added `spawn()` method to merge `overrides` Dict property through system

### Changed
- **Architectural Naming Standard**: Renamed all "Orchestrator" facades to "Managers" (`ResourceManager`, `SessionManager`) to clarify their roles as subsystem caretakers.
- **Documentation Consolidation**: Reorganized the `docs/` directory into conventional hierarchies, removing redundant "as-built" and "implementation" folders.
- **StreamManager Refinement**: Fully refactored the `StreamManager` use-case to delegate "What" (Identity/Policy) to the `ResourceManager` and "How" (Settings/Context) to the `SessionManager`.
- **Identity Registration:** Removed `ProtocolRegistration` dataclass and replaced with `AdapterBlueprint`

### Fixed
- **SessionContext:** Now carries `overrides` through system from `Gateway()` to call_level methods
- **Adapters**: Refactored to accept ResourceIdentity types
- **Registration Holes**: Closed the configuration gaps in `StreamManager.add_resource()` and implemented the delegation logic in `ResourceManager`.
- **Lifecycle Management**: Implemented a robust `teardown` sequence in the `Bootstrap` class for graceful resource release.

## [0.9.0] - 2026-03-19
### Changed
- Ret-conned versioning strategy to reflect the pre-Slalom experimental phase as `0.x.x`.
- Consolidation of the identity refactor and session context work into the final alpha milestone.

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
