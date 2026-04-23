---
id: HT-MANAGE-GITHUB
title: "How to Manage GitHub Issues and the Project Ledger"
status: stable
created_at: 2026-04-17
updated_at: 2026-04-23
component: core
type: how-to
---

# How to Manage GitHub Issues

Follow these steps to decompose your design into actionable tasks for Slalom ETL-Pipeline and maintain the Project Ledger.

## 1. Decompose the Work
*   Open your approved TDD and look at the **Detailed Design**.
*   Identify atomic units of work (e.g., "Create Packet Model," "Write fsspec Wrapper," "Register HTTP Adapter").

## 2. Issue Anatomy Mandate
To maintain high-signal communication and strict traceability, every issue (Epic, Feature, or Task) MUST contain the following three sections in its description:

*   **Description:** A concise summary of the context and technical rationale.
*   **Goal:** A definitive statement of what "Done" looks like for this specific unit of work.
*   **Steps:** An explicit Markdown Checklist (`- [ ]`) detailing the sequence of actions required for implementation.

## 3. GitHub UI: Create Tasks
1.  **Open Feature Issue:** Open the `Feature` issue created in the TDD phase.
2.  **Define Sub-Tasks:** In the issue description, list all atomic units of work using the **Steps** checklist format.
3.  **Convert to Issue:** Hover over each checklist item and click the **Convert to Issue** icon. This ensures that every sub-task is automatically linked to the parent feature.
4.  **Enforce Anatomy:** Once converted, open the new sub-task issue and ensure it is updated to include its own **Description** and **Goal**.

## 4. Fill the Metadata Ledger
For every task issue created:
1.  **Navigate to Project Board:** Open the [Slalom Project](https://github.com/users/mnaatjes/projects/4) (Table View).
2.  **Assign Custom Fields:**
    *   **Type:** Set to `Task`.
    *   **ADR Link:** Paste the link to the parent ADR file in the repo.
    *   **TDD Link:** Paste the link to the parent TDD file in the repo.
    *   **Component:** Select the appropriate domain (core, engine, ui).
    *   **Cycle:** Assign to the current iteration.

## 5. Verify Compliance
*   **Switch View:** Go to the **Audit (Compliance)** view on the project board.
*   **Check:** Ensure no issues have empty link fields.
