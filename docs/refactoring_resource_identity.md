# Refactoring Guide: Resource Identity Subsystem

This document outlines the steps required to migrate the codebase from the legacy `__resource_identity` (deprecated) to the new `resource_identity` subsystem.

---

## 1. Type Mapping

| Legacy Class (Deprecated) | New Class (Replacement) | Realm Context |
| :--- | :--- | :--- |
| `ResourceIdentity` | `ResourceIdentity` | Base Class (Updated) |
| `ResourceIdentifier` | `Address` | The "Intent" |
| `StreamLocation` | `Coordinate` | The "Reality" |
| `LogicalURI` | `VirtualAddress` | For `registry://` |
| `LogicalURI` | `LocalAddress` | For `posix://` |
| `PhysicalPath` | `LocalCoordinate` | Verified File Path |
| `PhysicalURI` | `NetworkAddress` | Unverified URL |
| `PhysicalURI` | `NetworkCoordinate` | Verified URL |
| `RemoteURL` | `NetworkCoordinate` | Specific URL |

---

## 2. Global Import Updates

All imports from `src.app.domain.models.__resource_identity` must be moved to `src.app.domain.models.resource_identity`.

**Old:**
```python
from src.app.domain.models.__resource_identity import StreamLocation, PhysicalPath
```

**New:**
```python
from src.app.domain.models.resource_identity import Coordinate, LocalCoordinate
```

---

## 3. Targeted Refactoring Locations

### A. Domain Services
- **`src/app/domain/services/resource_identity/catalog.py`**
  - Update `resolve_uri` signature: `Address` -> `Coordinate`.
  - Replace `LogicalURI` with `VirtualAddress` or `LocalAddress`.
  - Replace `PhysicalPath` with `LocalCoordinate`.
- **`src/app/domain/services/resource_identity/factory.py`**
  - Update `build` signature to return `Coordinate`.
  - Logic update: Use realm-specific classes (e.g., `LocalAddress`, `NetworkAddress`) during classification.
- **`src/app/domain/services/resource_identity/orchestrator.py`**
  - Implement the promotion logic using the new classes.

### B. Ports & Adapters
- **`src/app/ports/input/resource_boundaries/`**
  - Refined into realm-specific ports: `LocalResourceBoundary`, `NetworkResourceBoundary`, etc.
  - `resolve` signature updated to use realm-specific `Address` and `Coordinate`.
- **`src/infrastructure/adapters/posix_file/boundary.py`**
  - Updated implementation to inherit from `LocalResourceBoundary` and return `LocalCoordinate`.
- **`src/infrastructure/adapters/http/boundary.py`**
  - New implementation inheriting from `NetworkResourceBoundary`.

### C. Use Cases
- **`src/app/use_cases/manager.py`** (StreamManager)
  - Update `_get_protocol_for_location` to check for `Coordinate` implementations.
  - Update `resolve` method signature.

---

## 4. Implementation Details

### Path Handling
The legacy `PhysicalPath` inherited from `pathlib.Path`. The new `LocalCoordinate` stores the path as a string in `raw_value`. 
- **Change:** Instead of `path.exists()`, use `os.path.exists(path.raw_value)` or wrap `raw_value` back into a `Path` object within the Adapter.

### Protocol Extraction
The new `ResourceIdentity` has a built-in `protocol` property. 
- **Benefit:** You no longer need to manually parse the scheme in many locations.

---

## 5. Cleanup
Once all references are updated and tests pass:
1. Delete `src/app/domain/models/__resource_identity/` directory.
2. Update `src/app/domain/models/resource_identity/__init__.py` to ensure all necessary classes are exported.
