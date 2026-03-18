# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- **ResourceOrchestrator Facade**: Implemented a single entry point for the identity subsystem to manage the full lifecycle: *Classify -> Resolve -> Map -> Validate*.
- **Refined ResourceBoundary Ports**: Created realm-specific input ports (`LocalResourceBoundary`, `NetworkResourceBoundary`, etc.) using the **Template Method** pattern for centralized security enforcement.
- **HttpResourceBoundary**: Dedicated adapter for URL security, implementing host-locking and protocol consistency.
- **As-Built Documentation**: Comprehensive "Source of Truth" guide for the identity subsystem taxonomy and genealogy (`docs/as_built/resource_identity.md`).
- **Unified Service Exports**: Clean entry point for identity services in `src/app/domain/services/resource_identity/__init__.py`.

### Changed
- **Registry-Driven Classification**: Refactored `ResourceFactory` to dynamically discover resource realms via the `StreamRegistry`, eliminating hardcoded protocol lists.
- **Protocol-Agnostic Catalog**: Updated `ResourceCatalog` to take precedence based on resource nicknames (keys), regardless of the URI protocol used.
- **DataStream Migration**: Updated the `DataStream` output port to strictly consume the new `Coordinate` model instead of legacy `StreamLocation`.
- **Infrastructure Refinement**: Thin-adapter refactor for `PosixResourceBoundary`, focusing on physical path math while the Port handles domain-level sanitization.

### Fixed
- **Absolute Path Injection**: Fixed a vulnerability in `LocalResourceBoundary` where absolute paths could be injected as sub-paths.
- **Host Redirection Hijacking**: Implemented "Authority Locking" in `NetworkResourceBoundary` to prevent unauthorized host redirection.
- **Redundant URL Segments**: Fixed a logic error in URL joining that caused duplicated path segments (e.g., `v1/v1/`).
- **Memory Constructor Mismatches**: Fixed argument errors in `Memory`, `Synthetic`, and `Virtual` coordinate constructors.

### Removed
- **Legacy Identity Models**: Deleted `LogicalURI`, `PhysicalPath`, and `PhysicalURI` (moved to `__resource_identity_legacy`).
- **Hardcoded Protocols**: Removed static protocol-to-realm mappings from the domain services.

## [## [Unreleased]] - 2026-03-04
### Added
- **Smart Gateway Pattern**: Evolved the framework from a proxy to an intelligent resource mediator.
- **Self-Aware Packets**: Replaced the legacy `Envelope` system with a high-resolution `Packet` model.
- **StreamHandle & Capacity**: Introduced introspection via `StreamHandle`, allowing users to query resource capabilities (`can_seek`, `is_writable`) before execution.
- **Unified StreamContext**: Implemented a "Passport" system for data, ensuring every byte is stamped with a `trace_id` and lineage.
- **Catalog-Aware Resolution**: Refactored `ResourceFactory` to allow intuitive URI schemes (e.g., `posix://key`) for registered resources.
- **Comprehensive Test Suite**: Rewrote the entire test suite (30+ tests) covering unit and integration scenarios without using `MagicMock`.

### Fixed
- **Circular Imports**: Resolved complex dependency loops between domain models and ports.
- **URI Integrity**: Switched to `urllib.parse` for standard-compliant identity extraction.
- **Changelog Automation**: Fixed the "Inception" bug in the `bumpversion` configuration.

## [1.2.1] - 2026-03-04
### Changed
- Refined the versioning workflow and documentation.
- Removed outdated `__src/` directory.
- Corrected bumpversion `CHANGELOG` behavior.
- Deleted `feat/middleware` branch after merge.

## [1.2.0] - 2026-03-04
### Added
- **Catalog-Aware Resolution**: Initial implementation of intelligent URI resolution.
- **Protocol Safelist**: Added a security firewall to prevent unrecognized URI schemes.
- **Dependency Injection**: Updated `Bootstrap` to wire the `StreamRegistry` into the `ResourceFactory`.

### Fixed
- **Requirements**: Added missing `httpx` dependency.
- **URI Pathing**: Fixed edge cases in `LogicalURI` sub-path extraction.

## [1.0.0] - 2026-03-03
### Added
- Initial release of the StreamFlow framework.
- Support for POSIX and HTTP adapters.
- Resource identity and boundary security.
- Composition Root (Bootstrap) architecture.
