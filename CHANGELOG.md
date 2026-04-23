# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-04-23
### Added
- **Architectural Rebirth (ADR-001)**: Pivoted the framework to a lean, functional ETL core.
- **Retained Core**: Migrated high-performance Packet models, Middleware Engine, and Streaming Adapters (HTTP/POSIX).
- **Flattened Orchestration**: Removed bureaucratic manager layers in favor of a direct, generator-based streaming pipeline.

### Removed
- **Identity Framework**: Deprecated the over-engineered Resource Identity subsystem (Realms/Addresses/Coordinates).
- **Manager Hierarchy**: Eliminated `Gateway`, `ResourceManager`, and `SessionManager` facades to reduce cognitive load.
