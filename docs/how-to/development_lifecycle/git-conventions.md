---
id: HT-GIT-CONVENTIONS
title: "How to Use Git and GitHub Conventions"
status: stable
created_at: 2026-04-17
updated_at: 2026-04-17
component: core
type: how-to
---

# How to Use Git and GitHub Conventions

Follow these steps to ensure your source control history adheres to the **Law of Provenance** and **Conventional Commits**.

## 1. Branching Strategy
Always start from a clean and updated `main` branch.

### Step 1: Update Main
```bash
git checkout main
git pull origin main
```

### Step 2: Create a Typed Branch
Use the naming convention: `type/ISS-ID-short-description`

*   **feat/**: Features (`feat/102-health-logic`)
*   **fix/**: Bugs (`fix/205-inventory-overflow`)
*   **docs/**: Documentation (`docs/ADR-013-event-schema`)
*   **refactor/**: Refactoring (`refactor/core-di`)
*   **police/**: CI/Tests (`police/linting-rules`)

```bash
git checkout -b feat/102-damage-metabolism
```

## 2. The Commit Handshake
We use **Conventional Commits** appended with the Issue ID.

### Format
`type(component): description (#ISS-ID)`

### Example
```bash
git commit -m "feat(health): implement damage metabolism logic (#102)"
```

### Common Types:
*   `feat`: A new feature
*   `fix`: A bug fix
*   `docs`: Documentation only changes
*   `style`: Changes that do not affect the meaning of the code (white-space, formatting, etc)
*   `refactor`: A code change that neither fixes a bug nor adds a feature
*   `test`: Adding missing tests or correcting existing tests
*   `chore`: Changes to the build process or auxiliary tools

## 3. Pull Requests and Merging

### Step 1: Push to Remote
```bash
git push origin <branch-name>
```

### Step 2: Open Pull Request
1.  Go to GitHub and click **Compare & pull request**.
2.  **Title:** Match your commit message (e.g., `feat(health): implement damage metabolism logic (#102)`).
3.  **Description:** Use the keyword `Closes #102` to automatically close the task on the ledger.
4.  **TDD Link:** Provide a link to the TDD being implemented.

### Step 3: Squash and Merge
1.  Wait for the **Architectural Police** (CI checks) to pass.
2.  Click the arrow next to "Merge pull request" and select **Squash and merge**.
3.  Ensure the final commit message includes the Issue ID.

## 4. Local Enforcement (Optional)
You can prevent accidental non-compliant pushes by adding a pre-push hook.

**File:** `.git/hooks/pre-push`
```bash
#!/bin/bash
branch_name=$(git symbolic-ref --short HEAD)

if [[ ! $branch_name =~ ^(feat|fix|docs|refactor|police)/[0-9]+-.* ]]; then
    echo "❌ ERROR: Branch name must follow 'type/ISS-ID-slug' convention."
    exit 1
fi
```
Make it executable: `chmod +x .git/hooks/pre-push`
