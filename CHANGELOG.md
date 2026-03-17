# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- **Realm-Based Resource Identity**: Replaced the legacy `Union` type-aliasing with a formal class hierarchy based on logical Realms (`LOCAL`, `NETWORK`, `MEMORY`, `SYNTHETIC`, `VIRTUAL`).
- **Address & Coordinate Taxonomy**: Introduced `Address` (Intent) and `Coordinate` (Reality) as the primary abstractions for resource lifecycle management.
- **Resource Identity Implementations**: Added specialized classes for each realm: `LocalAddress/Coordinate`, `NetworkAddress/Coordinate`, `MemoryAddress/Coordinate`, `SyntheticAddress/Coordinate`, and `VirtualAddress/Coordinate`.
- **Refactoring Strategy**: Created a comprehensive guide (`docs/refactoring_resource_identity.md`) for migrating the codebase to the new `ResourceIdentity` subsystem.

### Changed
- **Genealogy Documentation**: Updated `resource_identity_genealogy.md` with the new Mermaid diagram, realm-based taxonomy, and `ResourceOrchestrator` service definition.
- **ResourceOrchestrator Role**: Formally defined the `ResourceOrchestrator` as a Domain Service responsible for the `Address -> Coordinate` promotion.

### Fixed
- **StreamHandle Lifecycle**: Corrected `StreamHandle.__enter__` to properly delegate to the adapter's context manager, ensuring the `is_open` flag is correctly set in the `DataStream` base class.

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
