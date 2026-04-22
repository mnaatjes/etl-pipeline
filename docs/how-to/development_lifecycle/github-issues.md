---
id: HT-MANAGE-GITHUB
title: "How to Manage GitHub Issues and the Project Ledger"
status: stable
created_at: 2026-04-17
updated_at: 2026-04-17
component: core
type: how-to
---

# How to Manage GitHub Issues

Follow these steps to decompose your design into actionable tasks and maintain the Project Ledger.

## 1. Decompose the Work
*   Open your approved TDD and look at the **Detailed Design**.
*   Identify atomic units of work (e.g., "Create Record DTO," "Write Pure Math Logic," "Register Service").

## 2. GitHub UI: Create Tasks
1.  **Open Feature Issue:** Open the `Feature` issue created in the TDD phase.
2.  **Tasklist:** In the issue description, click the **Add Tasklist** button.
3.  **Add Items:** Type the name of each task. GitHub will allow you to convert these into individual issues.
4.  **Convert to Issue:** Hover over a task and click the **Convert to Issue** icon.

## 3. Fill the Metadata Ledger
For every task issue created:
1.  **Navigate to Project Board:** Open the **Oregon Trail Project** (Table View).
2.  **Assign Custom Fields:**
    *   **Type:** Set to `Task`.
    *   **ADR Link:** Paste the link to the parent ADR file in the repo.
    *   **TDD Link:** Paste the link to the parent TDD file in the repo.
    *   **Component:** Select the appropriate "Screaming" domain.
    *   **Cycle:** Assign to the current iteration.

## 4. Verify Compliance
*   **Switch View:** Go to the **Audit (Compliance)** view on the project board.
*   **Check:** Ensure no issues have empty link fields.
