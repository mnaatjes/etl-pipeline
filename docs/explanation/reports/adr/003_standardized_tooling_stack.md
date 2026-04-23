---
id: ADR-003
title: "Adopt Standardized Tooling Stack for Lean Core"
status: proposed
created_at: 2026-04-23
updated_at: 2026-04-23
component: core
type: "explanation/adr"
epic_link: "https://github.com/mnaatjes/etl-pipeline/issues/15"
---

# Context

Slalom v0.9.0 suffered from significant architectural bloat, manual validation loops, and complex manager hierarchies. To fulfill the "Lean Rebirth" mandate (ADR-001), we require a modernized tooling stack that replaces custom, high-maintenance code with industry-standard libraries.

# Decision

We will adopt a standardized Python tooling stack focused on functional simplicity, strict boundary enforcement, and high-performance validation.

### Core Tooling Stack:

1. **fsspec (Filesystem Spec):**
   - **Role:** The Unified I/O Engine.
   - **Impact:** Replaces the 11-file `ResourceIdentity` subsystem and the `ResourceManager`. Provides a protocol-agnostic API for `file://`, `https://`, `s3://`, etc., returning standard file-like objects to the Domain.

2. **Pydantic v2:**
   - **Role:** The Contract Authority.
   - **Impact:** Replaces manual `StreamContract` loops and `__post_init__` type-guards. Leverages Rust-backed performance to ensure every `Packet` and `Config` object is valid without custom defensive logic.

3. **pytest-archon:**
   - **Role:** The Boundary Police.
   - **Impact:** Implements automated "Fitness Functions." Programmatically ensures that the Domain layer remains free of Infrastructure imports, preventing the "Symmetric Delegation" mess of v0.9.0.

4. **structlog:**
   - **Role:** High-Signal Traceability.
   - **Impact:** Replaces manual `trace_id` propagation. Allows binding metadata to context-local loggers, collapsing 3+ manager layers into a single observability pattern.

5. **more-itertools:**
   - **Role:** Functional Pipeline Utilities.
   - **Impact:** Provides professional generator utilities for chunking, flattening, and windowing, ensuring the `MiddlewareEngine` remains lean and readable.

6. **Typeguard:**
   - **Role:** Runtime Enforcement.
   - **Impact:** Used during development to ensure implementation stubs strictly adhere to the Abstract Base Class (Port) definitions defined in the Outside-In strategy (ADR-002).

# Comparison of Complexity (Tooling ROI)

| Issue in v0.9.0 | Tool Solution | Impact on Codebase |
| :--- | :--- | :--- |
| **URI/Path Logic** | `fsspec` | -1,500 lines of custom code |
| **Validation Loops** | `Pydantic` | -500 lines of defensive logic |
| **Manager Chains** | `structlog` | Collapses 3 Manager layers into 1 |
| **Boundary Drift** | `pytest-archon` | Zero "Manual Audit" overhead |

# Consequences

### Positive
- **Reduced Maintenance:** Shifting responsibility for low-level I/O and validation to well-maintained upstream libraries.
- **Improved Reliability:** Automated boundary enforcement prevents structural decay over time.
- **Developer Productivity:** Standard APIs (fsspec, Pydantic) reduce the learning curve for new contributors.

### Negative
- **Dependency Management:** Increased reliance on external libraries.
- **Learning Curve:** Requires familiarity with Pydantic v2 and generator-based functional programming.
