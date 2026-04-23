# PROJECT MANDATE: ETL-Pipeline "Slalom" — Continuity & Architectural Audit

1. Primary Objective

Perform a comprehensive "Intended vs. Actual" gap analysis to provide a data-driven recommendation: Refactor (Continue) or Rebuild (Start Fresh). The decision must be based on technical debt density, architectural drift, and cognitive complexity.

2. Assessment Criteria (The Mandate)

The audit must evaluate the codebase against the following immutable standards:

    Hexagonal Boundaries: Verify strict isolation of the Domain layer. Identify any "leaky abstractions" where infrastructure (e.g., networking, database logic) has infiltrated business logic.

    SOLID Compliance: Specifically audit the Single Responsibility Principle (class bloat) and Dependency Inversion (tight coupling).

    Contract-First Integrity: Assess if Pydantic models and interfaces (ABCs) serve as the source of truth, or if implementation detail has superseded the contract.

    Project Bloat: Identify "Dead Code," redundant dependencies, and unused utility modules that contribute to cognitive load.

3. Agent Instructions: The Audit Workflow

    Ingestion: Scan /src and /tests to map the current dependency graph and module hierarchy.

    Entity Interrogation: Systematically question components:

        Which architectural mandate is most difficult to satisfy in the current state?

        Where do anti-patterns (e.g., God Objects, Spaghetti Code) appear?

        Is the testing suite (/tests) comprehensive enough to support a safe refactor?

    Gap Analysis: Contrast the Actual implementation with the Intended Hexagonal/SOLID architecture.

4. Synthesis & Recommendation Schema

At the conclusion of the audit, the agent must generate an AAR (After Action Report) using the following schema:

```yml
AAR:
  description: "Slalom Continuity Recommendation"
  objective: "Determine Refactor vs. Rebuild viability"
  directives:
    - evidence_based: "Every claim must be supported by specific documentation lines or commit hashes."
    - actionable_output: "The goal is a definitive path forward, not a general summary."
  results:
    intended_vs_actual: "Analysis of the architectural gap."
    bloat_assessment: "Identification of redundant or high-complexity modules."
  recommendation:
    path: "[REFACTOR | REBUILD]"
    justification: "Quantitative and qualitative reasoning based on audit findings."
    risk_level: "[LOW | MEDIUM | HIGH]"
  workflow:
    - 1: "Immediate corrective actions (if Refactor)"
    - 2: "Foundational requirements (if Rebuild)"
```

5. User Constraints

    No Autonomous Execution: All findings are recommendations only. Do not modify files.

    Educational Context: Explain why a specific pattern is failing, focusing on the mechanism of the failure to aid user comprehension.

    Bureaucratic Precision: Adhere strictly to the defined AAR schema and file pathing: docs/explanation/reports/aar/.