---
id: HT-DRAFT-TDD
title: "How to Draft a Technical Design Document (TDD)"
status: stable
created_at: 2026-04-17
updated_at: 2026-04-23
component: core
type: how-to
---

# How to Draft a TDD

Follow these steps to define the "How" of a feature for Slalom ETL-Pipeline after the "Why" has been established in an ADR.

## 1. Initialize the Design
*   **Prerequisite:** The parent ADR must be in `Adopted` or `Proposed` status.
*   **Location:** Create a new Markdown file in `docs/explanation/design/tdd/`.
*   **Naming:** Use kebab-case (e.g., `fsspec-io-integration.md`).
*   **Frontmatter:** Initialize with the required metadata:
    ```yaml
    id: TDD-XXX
    parent_adr: ADR-XXX
    title: "TDD: Feature Name"
    status: pending
    created_at: YYYY-MM-DD
    updated_at: YYYY-MM-DD
    component: core | engine | ui | domain:<name>
    type: "explanation/design"
    feature_link: PENDING
    ```

## 2. Define the Specification
*   **Overview:** Summarize the goal.
*   **Proposed Design:** Include Mermaid diagrams (Component and Sequence).
*   **Detailed Design:** Define data schemas, class signatures, and interface protocols.
*   **Goal:** Ensure an LLM or developer can write implementation stubs from this section alone.

## 3. GitHub UI: Create the Feature Issue
1.  **Navigate:** Go to the [Slalom ETL-Pipeline Repository](https://github.com/mnaatjes/etl-pipeline.git).
2.  **Create Issue:** Click the **Issues** tab -> **New Issue**.
3.  **Title:** Use the TDD ID and Title (e.g., `[TDD-001] fsspec Integration`).
4.  **Label:** Apply the `Feature` label.
5.  **Project:** Assign the issue to the [Slalom Project](https://github.com/users/mnaatjes/projects/4).
6.  **Hierarchy:** In the **Parent** field on the right sidebar, select the **Epic Issue** corresponding to the parent ADR.
7.  **Copy URL:** Copy the issue URL.

## 4. Finalize the Traceability
*   **Update Frontmatter:** Replace `feature_link: PENDING` with the URL of the GitHub Issue.
