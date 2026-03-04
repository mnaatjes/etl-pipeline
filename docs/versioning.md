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
3. **Target Files:** Which files to update (e.g., `src/__init__.py`, `README.md`, `src/app/__init__.py`).

### The Versioning Workflow (What you actually do)

When you are ready to update the version, you **do not** manually edit any files. Instead, follow these steps:

1.  **Select Change Type:** Decide if your change is a `major`, `minor`, or `patch`.
2.  **Execute the Command:** Run the command in your terminal:
    ```bash
    bumpversion <part>  # where <part> is major, minor, or patch
    ```
3.  **Automatic Synchronization:** The tool will:
    - Update `current_version` in `.bumpversion.cfg`.
    - Update `__version__` in `src/__init__.py` and `src/app/__init__.py`.
    - Update the version badge in `README.md`.
    - Stage the changes, commit them with a version message, and create a Git tag (e.g., `v1.2.0`).

### Maintenance of `.bumpversion.cfg`
- **When adding new files:** If you create a new file that needs to display the version number, add a new `[bumpversion:file:path/to/file]` block to `.bumpversion.cfg`.
- **When changing README format:** If you change the style of the version badge in the `README.md`, update the `search` and `replace` patterns in the config file.

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

## 6. Summary: How to Push an Update

1. **Finalize Code:** Ensure `feat/middleware` is clean.
2. **Merge:** Merge into `main`.
3. **Bump:** Run `bumpversion minor` (updates files, commits, tags).
4. **Changelog:** Run `towncrier build` to compile fragments.
5. **Push:** `git push origin main --tags`.
