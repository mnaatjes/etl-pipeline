---
id: HT-PR-AND-MERGE
title: "How to Perform Pull Requests and Squash Merges"
status: stable
created_at: 2026-04-18
updated_at: 2026-04-18
component: core
type: how-to
---

# Pull Requests and Squash Merges

In the Oregon Trail development lifecycle, the **Pull Request (PR)** is the "Gate" through which all code must pass. The **Squash Merge** is the "Polishing" step that keeps our project history clean and readable.

## 1. The Pull Request (PR) Workflow

A Pull Request is a formal proposal to merge a feature branch into `main`.

### Step-by-Step (GitHub Web UI)
1.  **Push your branch:** Ensure your local work is pushed to GitHub (`git push origin <branch-name>`).
2.  **Open PR:** On GitHub, click **Compare & pull request**.
3.  **Title:** Use the Conventional Commits format: `type(component): description (#ISSUE-ID)`.
4.  **Chain of Custody:** In the right sidebar, under **Development**, link the corresponding GitHub Issue(s).
5.  **Review:** Ensure all CI checks (Architectural Police, Tests) are green.

## 2. The Squash and Merge Strategy

When a PR is approved, we use the **Squash and Merge** strategy rather than a standard merge commit.

### What it does:
It takes all the individual commits on your feature branch (e.g., "fix typo," "added model," "temp save") and combines them into **one single, high-level commit** on the `main` branch.

### Use Cases:
*   **Maintaining a Clean History:** It prevents `main` from being cluttered with "messy" development commits.
*   **Atomic Reverts:** If a feature causes a bug, you can revert the entire feature with one click because it exists as a single commit on `main`.
*   **Traceability:** The single squashed commit preserves the PR number and a list of all original contributors.

## 3. Local Cleanup (The "Force Delete" Flag)

After a Squash Merge, your local Git will often report an error when you try to delete the feature branch:
`error: the branch 'branch-name' is not fully merged.`

### Why?
Because the commit IDs on your local branch no longer match the new "Squashed" commit ID on `main`. Git thinks you are about to lose work.

### The Solution:
Once you have pulled the latest `main`, use the capital **-D** flag to force the deletion:
```bash
git checkout main
git pull origin main
git branch -D <feature-branch-name>
```

## 4. Summary Table

| Action | When to use | Why |
| :--- | :--- | :--- |
| **Pull Request** | Every time you finish a Task. | To ensure the Law of Verification and provenance. |
| **Squash Merge** | To finalize a PR. | To keep `main` history professional and readable. |
| **Branch -D** | After merging to `main`. | To clean up local branches that were squashed. |
