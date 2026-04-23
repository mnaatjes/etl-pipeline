---
id: HT-CREATE-ADR
title: "How to Create an Architectural Decision Record (ADR)"
status: stable
created_at: 2026-04-17
updated_at: 2026-04-23
component: core
type: how-to
---

# How to Create an ADR

Follow these steps to propose and document a strategic architectural decision for the Slalom ETL-Pipeline.

## 1. Identify and Research
*   **Identify:** Recognize an architectural requirement or a change in the project's "Laws of Physics."
*   **Research:** Validate your assumptions and explore alternatives using the `codebase_investigator`.

## 2. Draft the Document
*   **Location:** Create a new Markdown file in `docs/explanation/reports/adr/`.
*   **Naming:** Use the naming convention `XXX_description.md` (e.g., `001_slalom_rebirth.md`).
*   **Frontmatter:** Initialize with the required metadata:
    ```yaml
    id: ADR-XXX
    title: "Clear, Concise Title"
    status: proposed
    created_at: YYYY-MM-DD
    updated_at: YYYY-MM-DD
    component: core | engine | ui | domain:<name>
    type: "explanation/adr"
    epic_link: PENDING
    ```

## 3. GitHub UI: Create the Epic Issue
To maintain the "Chain of Custody," you must link the document to a tracking issue.
1.  **Navigate:** Go to the [Slalom ETL-Pipeline Repository](https://github.com/mnaatjes/etl-pipeline.git).
2.  **Create Issue:** Click the **Issues** tab -> **New Issue**.
3.  **Title:** Use the ADR ID and Title (e.g., `[ADR-001] Pivot to Lean Streaming`).
4.  **Label:** Apply the `Epic` label.
5.  **Project:** On the right sidebar, assign the issue to the [Slalom Project](https://github.com/users/mnaatjes/projects/4).
6.  **Copy URL:** Copy the URL of the newly created issue.

## 4. Finalize the Traceability
*   **Update Frontmatter:** Replace `epic_link: PENDING` with the URL of the GitHub Issue.
*   **Update updated_at:** Set the date to today.
