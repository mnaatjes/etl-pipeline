---
id: HT-WORKFLOW-CHEAT-SHEET
title: "Trail Map: The Workflow Cheat Sheet"
status: stable
created_at: 2026-04-18
updated_at: 2026-04-18
component: core
type: how-to
---

# The Workflow Trail Map (Cheat Sheet)

Use this shorthand guide to move from a Strategic Idea to a Verified Line of Code.

## Phase 1: Strategic (The ADR)
1.  **Draft:** Create `docs/explanation/reports/adr/XXX_name.md`.
2.  **ID:** Assign `ADR-XXX`. Set `status: proposed`.
3.  **Epic:** `gh issue create --title "[ADR-XXX] Title" --label "Epic,Type: Architecture" --project "Oregon Trail Project"`
4.  **Link:** Paste the Issue URL into `epic_link` in the ADR file.
5.  **Adopt:** Once approved, set `status: adopted`.

## Phase 2: Tactical (The TDD)
1.  **Draft:** Create `docs/explanation/design/name.md`.
2.  **ID:** Assign `TDD-XXX`. Set `parent_adr: ADR-XXX`.
3.  **Feature:** `gh issue create --title "[TDD-XXX] Title" --label "feature,Type: Architecture" --project "Oregon Trail Project"`
4.  **Link Feature:** Update `feature_link` in the TDD file.
5.  **Parent to Epic:** Add `- [ ] #FeatureID` to the ADR-Epic Issue description.

## Phase 3: Operational (The Task)
1.  **Decompose:** Inside the TDD-Feature issue, add `- [ ] Task Name`.
2.  **Convert:** Hover the task and click "Convert to Issue".
3.  **Audit:** Go to the Project Board and fill in the `ADR Link` and `TDD Link` for the new Task row.

## Phase 4: Implementation (The PR)
1.  **Branch:** `git checkout -b type/ISSUE-ID-slug` (e.g., `feat/22-root-contract`).
2.  **Code:** Follow the TDD spec strictly.
3.  **PR:** Create a PR titled `type(component): description (#ISSUE-ID)`.
4.  **Close:** Ensure the PR description says `Closes #ISSUE-ID`.
5.  **Merge:** Squash and Merge.

---
**Golden Rule:** If the Project Ledger (Table View) has an empty Link column, the "Chain of Custody" is broken. Fix it before merging.
