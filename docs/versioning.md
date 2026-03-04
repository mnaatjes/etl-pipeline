# Versioning Strategy & Execution

This document defines the versioning standards and automated release workflows for the StreamFlow framework.

## 1. Semantic Versioning (SemVer)

StreamFlow follows [SemVer 2.0.0](https://semver.org/): `MAJOR.MINOR.PATCH` (e.g., `v1.2.3`).

- **MAJOR (X.y.z):** Breaking changes. Used when API contracts change or legacy features are removed (e.g., transitioning from `Envelope` to `Packet`).
- **MINOR (x.Y.z):** New features. Backwards-compatible functionality additions (e.g., adding a new Cloud adapter).
- **PATCH (x.y.Z):** Bug fixes. Backwards-compatible fixes or internal refactoring (e.g., fixing a path resolution edge case).

---

## 2. Release Workflow

### Step 1: Feature Branch Completion
All work is performed on feature branches (e.g., `feat/middleware`).
- Ensure all tests pass: `pytest tests/unit tests/integration`.
- Update documentation in `docs/` and `README.md`.

### Step 2: Merge to Main
1. Checkout `main`: `git checkout main`.
2. Pull latest: `git pull origin main`.
3. Merge feature branch: `git merge feat/middleware`.
4. Resolve any conflicts and run tests again.

### Step 3: Version Bump & Tagging
1. Determine the new version number based on the changes.
2. Update the version in the **Single Source of Truth (SSoT)**: `pyproject.toml` (and `src/__init__.py` if applicable).
3. Commit the version bump: `git commit -am "chore: bump version to v1.1.0"`.
4. Create a Git Tag: `git tag -a v1.1.0 -m "Release v1.1.0: Middleware Refactor"`.
5. Push changes and tags: `git push origin main --tags`.

---

## 3. Automation Tools

To maintain consistency and automate the "Toilsome" parts of releasing, we use the following stack:

### Hatch (Build & Version Management)
Hatch is our primary build backend. It can manage dynamic versions.
- **Installation:** `pip install hatch`
- **Usage:** Hatch reads `pyproject.toml`. To see the current version: `hatch version`.

### Towncrier (Changelog Management)
Towncrier prevents merge conflicts in `CHANGELOG.md` by using "fragments."
- **Installation:** `pip install towncrier`
- **Usage:**
    1. Create a fragment: `towncrier create 123.feature.md -m "Added Catalog-Aware resolution"`.
    2. Build changelog: `towncrier build --version v1.1.0`.

### Bumpversion / Bump2version (Syncing)
Used to ensure the version string is updated across multiple files (README, pyproject, code).
- **Installation:** `pip install bump2version`
- **Usage:** `bumpversion minor` (automatically increments version, commits, and tags).

---

## 4. Configuration (pyproject.toml)

Our `pyproject.toml` should be configured to support these tools:

```toml
[project]
name = "streamflow-framework"
version = "1.1.0" # Managed by bumpversion or hatch

[tool.hatch.version]
path = "src/app/__init__.py" # SSoT for the code
```

---

## 5. Summary: How to Push an Update

1. **Finalize Code:** Ensure `feat/middleware` is clean.
2. **Merge:** Merge into `main`.
3. **Bump:** Run `bumpversion minor` (updates files, commits, tags).
4. **Changelog:** Run `towncrier build` to compile fragments.
5. **Push:** `git push origin main --tags`.
