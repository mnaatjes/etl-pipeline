# Versioning Strategy & Execution

This document defines the versioning standards and automated release workflows for the StreamFlow framework.

## 1. Semantic Versioning (SemVer)

StreamFlow follows [SemVer 2.0.0](https://semver.org/): `MAJOR.MINOR.PATCH` (e.g., `v1.2.3`).

- **MAJOR (X.y.z):** Breaking changes. Used when API contracts change or legacy features are removed (e.g., transitioning from `Envelope` to `Packet`).
- **MINOR (x.Y.z):** New features. Backwards-compatible functionality additions (e.g., adding a new Cloud adapter).
- **PATCH (x.y.Z):** Bug fixes. Backwards-compatible fixes or internal refactoring (e.g., fixing a path resolution edge case).

---

## 2. Release Workflow

### Step 1: Document Your Changes
As you develop on your feature branch, add your release notes to the **`CHANGELOG.md`** file under the `## [Unreleased]` section.

**Example `CHANGELOG.md` during development:**
```markdown
## [Unreleased]
### Added
- New S3 Adapter for cloud storage.
- Capability discovery for stream seeking.
```

### Step 2: Merge to Main
1. Ensure all tests pass: `pytest tests/unit tests/integration`.
2. Checkout `main` and merge your feature branch:
   ```bash
   git checkout main
   git merge feat/your-feature-branch
   ```

### Step 3: Execute the Automated Bump
Run the `bumpversion` command with the appropriate part (`major`, `minor`, or `patch`).

```bash
./.venv/bin/bumpversion minor
```

**What this does:**
1.  **Calculates** the new version (e.g., `1.2.0`).
2.  **Syncs** all version strings in code, `README.md`, and `.bumpversion.cfg`.
3.  **Stamps** the `CHANGELOG.md` by moving the notes from `[Unreleased]` into a new `[1.2.0]` section with today's date.
4.  **Commits** and **Tags** the release in Git automatically.

### Step 4: Push to Remote
Push your newly created commit and tag to the repository.
```bash
git push origin main --tags
```

---

## 3. Automation Tools

To maintain consistency and automate the "Toilsome" parts of releasing, we use the following stack:

### Hatch (Build & Version Management)
Hatch is our primary build backend. It can manage dynamic versions.
- **Usage:** Hatch reads `pyproject.toml`. To see the current version: `hatch version`.

### Bumpversion / Bump2version (Syncing & Tagging)
Used to ensure the version string is updated across multiple files and to handle Git tagging.
- **Usage:** `./.venv/bin/bumpversion [major|minor|patch]`

---

## 4. Single Source of Truth (SSoT)

The definitive location for the version number is **`src/__init__.py`**. 
- **Code:** Access via `import src; print(src.__version__)`.
- **Packaging:** `pyproject.toml` is configured to pull the version dynamically from this file.
- **Automation:** The `.bumpversion.cfg` file acts as the **Workflow Governor**, keeping all files in sync.

---

## 5. Automation with `bumpversion`

We use `.bumpversion.cfg` to automate the propagation of the version string across the codebase.

### The `.bumpversion.cfg` Configuration
This file tracks:
1. **The Current Version:** (e.g., `1.1.0`)
2. **Commit/Tagging:** Whether to automatically commit changes and create a Git tag.
3. **Target Files:** Which files to update (e.g., `src/__init__.py`, `README.md`, `src/app/__init__.py`, `CHANGELOG.md`).

---

## 6. Configuration (pyproject.toml)

Our `pyproject.toml` is configured to use **Hatch** as the build backend, which pulls the version from the SSoT:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "streamflow-framework"
dynamic = ["version"]

[tool.hatch.version]
path = "src/__init__.py"
```

---

## 7. Summary: How to Push an Update

1.  **Finalize Code:** Ensure your feature branch is clean and tested.
2.  **Document:** Add bullet points to `CHANGELOG.md` under `## [Unreleased]`.
3.  **Merge:** `git checkout main && git merge <branch>`.
4.  **Bump:** `./.venv/bin/bumpversion [major|minor|patch]`.
5.  **Push:** `git push origin main --tags`.
