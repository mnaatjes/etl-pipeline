# Status Report: Protocol Identity Conflict

**Date:** 2026-03-28  
**Priority:** High (Potential for Runtime Crashes)  
**Component:** Resource Identity / Stream Registry

## 1. Issue Description
A "Protocol Identity Conflict" occurs when the **Logical Layer** (the name given to a driver during registration) does not match the **Physical Layer** (the scheme prefix in a URI).

### Example of the Conflict:
```python
# User registers a resource as 'posix' but provides a 'file://' anchor
app.add_resource(key="data", protocol="posix", anchor="file:///srv/data")

# 1. Discovery Snapshot reports:
app.get_resource("data")["protocol"]  # returns 'posix'

# 2. Coordinate Resolution reports:
app.resolve("file:///srv/data").protocol  # returns 'file' (from URI scheme)
```

**The Danger:** If the `StreamRegistry` is asked for an adapter for `file`, but it only knows about `posix`, the framework will raise a `KeyError`, even though both refer to the same physical driver.

## 2. Root Cause
The `Coordinate` object extracts its `protocol` property directly from the URI string (the scheme). It is currently unaware of the **Implementation Protocol** (the driver name) used in the `ResourceCatalog` and `StreamRegistry`.

## 3. Proposed Solutions

### Solution A: The "Scheme Alias" System (Recommended)
Update the `StreamRegistry` to allow multiple schemes to point to the same driver.
*   **Pros:** High flexibility; users can use `file://`, `posix://`, or even `local://` interchangeably.
*   **Cons:** Increases complexity of the Registry logic.

### Solution B: Formalize Terminology (The 3-Way Map)
Introduce a distinction in the `Coordinate` and `ResourceIdentity` models between:
1.  **Scheme:** The URI prefix (`file://`).
2.  **Implementation Protocol:** The technical driver key (`posix`).
3.  **Adapter:** The Python class (`PosixFileAdapter`).

*   **Pros:** Correct architectural resolution; removes ambiguity entirely.
*   **Cons:** Requires a refactor of core identity value objects.

### Solution C: Strict Registration Alignment (Short-term)
Enforce that the `protocol` argument in `add_resource()` must exactly match the `scheme` used in the anchor URI.
*   **Pros:** No code changes required; simple documentation fix.
*   **Cons:** Brittle; users will frequently make mistakes (e.g., using `s3` for `s3n` or `s3a` URIs).

## 4. Immediate Mitigation
Until a structural solution is implemented, users are advised to ensure that their **Registration Protocol** string matches their **URI Scheme** prefix exactly.
