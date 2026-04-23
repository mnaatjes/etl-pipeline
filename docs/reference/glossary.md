# Glossary Reference

This document defines the technical vocabulary for the Slalom ETL-Pipeline framework.

### Core Concepts

1.  **Smart Packet:** The immutable unit of work that carries payload, metadata, and lineage across the transformation chain.
2.  **Framework Gateway:** The singular `Slalom` entry point that orchestrates the building and execution of pipelines.
3.  **Port:** An abstract interface (ABC) that defines the required behavior for an extension (e.g., a source, a sink, or a filter).
4.  **Adapter:** A physical implementation of a Port that interacts with external side-effects (e.g., HTTP, POSIX Filesystem).
5.  **Pipeline Builder:** A fluent DSL state-collector used to construct a type-safe transformation sequence.
6.  **Middleware Engine:** The recursive transformation logic that drives packets through a chain of processors.

### Technical Terms

*   **Outside-In Design:** The strategy of prioritizing public API ergonomics and internal contracts before building physical infrastructure.
*   **Fitness Function:** An architectural unit test that programmatically enforces system boundaries (e.g., Hexagonal isolation).
*   **Path Sandboxing:** The security practice of jailing I/O operations to a specific physical root (Anchor).
