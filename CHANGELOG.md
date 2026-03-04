# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Changed
- Refined the versioning workflow and documentation.
- Removed outdated `_src/` dir
- Corrected bumpversion `CHANGELOG` behavior
- Deleted feat/middleware branch after merge

## [1.2.0] - 2026-03-04

### Added
- **Catalog-Aware Resolution**: The `ResourceFactory` now intelligently resolves URIs based on registered catalog anchors.
- **Smart Gateway Pattern**: Evolved the `StreamClient` to act as an intelligent mediator for resource access.
- **Unified LogicalURI**: Refactored `LogicalURI` to use `urllib.parse` for standard-compliant URI handling.
- **Protocol Safelist**: Added a security firewall to `ResourceFactory` to prevent unrecognized URI schemes.
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
