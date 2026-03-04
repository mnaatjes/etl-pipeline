# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.2] - 2026-03-04
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
