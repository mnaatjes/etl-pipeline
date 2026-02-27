# Architectural Philosophy: Project vs. Platform

This document defines the "Refactoring Crossroads" that transitions the pipeline engine from a simple project to a robust platform. The core principle is the separation of the **Regime** (what should happen) from the **Execution** (how it happens).

## 1. Semantic Realignment: "Jobs" vs. "Runners"
In professional data engineering, the term "Runner" is typically reserved for the infrastructure agent (the physical process or container). The logic defining how data moves is a **Job** or **Workflow**.

- **Action:** Rename `src/app/pipelines/` to `src/app/jobs/`.
- **Definition:** A "Job" is a versioned, repeatable unit of work that takes specific inputs and produces outputs (similar to Dagster's terminology).

## 2. The Separation of Powers (The Three Roles)
To avoid "God Objects," the architecture is split into three distinct roles:
1. **The Context (The "Regime"):** `AppConfig` and `StreamContract`. Pure data structures representing static rules (env, log levels).
2. **The Registry (The "Librarian"):** An infrastructural component that holds a catalog of available adapters (Local, HTTP).
3. **The Bootstrap (The "Assembler"):** A service that takes the Context, consults the Registry, and assembles ready-to-use streams.

## 3. Structural Map

| Entity | Location | Responsibility | User Interaction |
| :--- | :--- | :--- | :--- |
| **AppConfig** | `src/app/ports/config.py` | Holds Static Rules (env, log_level). | Provided at startup. |
| **StreamRegistry** | `src/infrastructure/registry.py` | Holds the Catalog of available adapters. | Infrastructural / Internal. |
| **Bootstrap** | `src/app/bootstrap.py` | The Assembler. Connects Config to Registry. | The primary entry point. |
| **Job** | `src/app/jobs/base.py` | The Executor. Moves data using streams. | Triggered by the user. |

## 4. Control Plane vs. Data Plane
This split creates a clear distinction:
- **Control Plane:** Configuration resolution and stream management (The "Regime").
- **Data Plane:** The actual movement of data through jobs and middleware (The "Execution").
