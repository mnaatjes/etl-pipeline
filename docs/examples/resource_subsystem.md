# Example Usage: Resource Identity Subsystem

This guide provides practical code examples for working with the refactored Resource Identity subsystem.

---

## 1. The Five Realms of Identity

The system classifies every resource into one of five mutually exclusive realms, each with its own `Address` (Intent) and `Coordinate` (Reality) classes.

### A. Local Realm (Filesystems)
Used for POSIX, Windows, or any hierarchical local storage.

```python
from src.app.domain.models.resource_identity import LocalAddress, LocalCoordinate

# INTENT: "I want to access this local path"
address = LocalAddress("posix:///tmp/scans/01.csv")

# REALITY: "The verified physical path"
coord = LocalCoordinate(path="/tmp/scans/01.csv", key="scans")
```

### B. Network Realm (URLs)
Used for HTTP, HTTPS, S3, FTP, etc.

```python
from src.app.domain.models.resource_identity import NetworkAddress, NetworkCoordinate

# INTENT: "I want to call this API"
address = NetworkAddress("https://api.example.com/v1/data")

# REALITY: "The verified URL"
coord = NetworkCoordinate(url="https://api.example.com/v1/data", key="api")
```

### C. Memory Realm (In-Process)
Used for RAM-based caches, buffers, or message queues.

```python
from src.app.domain.models.resource_identity import MemoryAddress, MemoryCoordinate

# INTENT: "I want this item from the cache"
address = MemoryAddress("memory://results/task-001")

# REALITY: "The memory reference/pointer"
coord = MemoryCoordinate(reference="results/task-001")
```

### D. Synthetic Realm (Generators)
Used for procedurally generated data (e.g., `range`, `faker`, `mock`).

```python
from src.app.domain.models.resource_identity import SyntheticAddress, SyntheticCoordinate

# INTENT: "Generate 100 rows of random data"
address = SyntheticAddress("synthetic://faker/users?count=100")

# REALITY: "The generator identifier"
coord = SyntheticCoordinate(generator_id="faker/users")
```

### E. Virtual Realm (Internal Aliases)
Used for the `registry://` protocol and logical overlays.

```python
from src.app.domain.models.resource_identity import VirtualAddress, VirtualCoordinate

# INTENT: "Resolve the 'scans' alias"
address = VirtualAddress("registry://scans/report.pdf")

# REALITY: "The resolved virtual path"
coord = VirtualCoordinate(virtual_path="registry/scans/report.pdf")
```

---

## 2. ResourceOrchestrator (The Facade)

The `ResourceOrchestrator` is the primary entry point for the application. It simplifies the multi-step promotion process into single method calls.

```python
from src.app.domain.services.resource_identity import ResourceOrchestrator

# 1. SETUP: Components are usually injected via a Container
orchestrator = ResourceOrchestrator(factory, catalog, registry)

# 2. PROMOTION: String -> Secured Coordinate
# This handles Classification, Catalog Lookup, and Boundary Resolution in one go.
uri = "registry://scans/01.csv"
coordinate = orchestrator.resolve_resource(uri)

print(f"Physical Reality: {coordinate.raw_value}") 
# Output: /srv/data/scans/01.csv (if registered as an anchor)

# 3. MAPPING: Coordinate -> Adapter Blueprint
# Find out HOW to talk to this resource.
registration = orchestrator.get_registration(coordinate.protocol)
adapter_cls = registration.adapter_cls

# 4. VALIDATION: Policy Check
# Ensure the coordinate doesn't violate security policies (Contextual Guard).
try:
    orchestrator.validate_policy(coordinate)
except PermissionError as e:
    print(f"Access Denied: {e}")
```

---

## 3. ResourceCatalog (The Librarian)

The Catalog is responsible for managing "Anchors" (Security Cages) and "Nicknames" (Keys).

```python
from src.app.domain.services.resource_identity import ResourceCatalog
from src.app.domain.models.resource_identity import LocalCoordinate, ResourceKey

catalog = ResourceCatalog()

# 1. Register a Boundary for a protocol
# Boundaries perform the actual 'joining' and 'security math'.
catalog.register("posix", PosixResourceBoundary())

# 2. Add an Anchor (Nickname -> Physical Root)
anchor = LocalCoordinate("/srv/data/scans")
catalog.add_anchor(ResourceKey("scans"), anchor)

# 3. Discovery
if catalog.has_resource("posix", "scans"):
    print("Catalog knows where 'scans' are located.")
```

---

## 4. ResourceBoundary (Infrastructure Implementation)

Implementing a new boundary for a specific adapter.

```python
from src.app.ports.input.resource_boundaries import LocalResourceBoundary
from src.app.domain.models.resource_identity import LocalAddress, LocalCoordinate

class MySpecialBoundary(LocalResourceBoundary):
    
    def _do_resolve(self, subpath: str, anchor: LocalCoordinate, address: LocalAddress) -> LocalCoordinate:
        """The mechanical joining logic"""
        # subpath is guaranteed clean by the Port
        joined = f"{anchor.raw_value}/{subpath}"
        return LocalCoordinate(path=joined, key=address.key)

    def is_safe(self, resource: LocalCoordinate, anchor: LocalCoordinate) -> bool:
        """Physical containment check"""
        return resource.raw_value.startswith(anchor.raw_value)
```
