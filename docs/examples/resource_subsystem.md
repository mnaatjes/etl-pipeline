# Example Usage: Resource Identity Subsystem

This guide provides practical code examples for working with the refactored Resource Identity subsystem.

---

## 1. Addresses & Coordinates
The foundational "Nouns" of the system.

### Creating an Intent (Address)
Addresses represent a logical request. They parse their own protocol and authority (key) from a URI string.

```python
from src.app.domain.models.resource_identity import VirtualAddress, LocalAddress

# A request for a managed resource
address = VirtualAddress("registry://scans/01.csv")
print(address.key)      # Output: "scans"
print(address.protocol) # Output: "registry"

# A request for a direct POSIX file
direct = LocalAddress("posix:///tmp/data.log")
print(direct.key)       # Output: "tmp" (from authority)
print(direct.protocol)  # Output: "posix"
```

### Creating a Reality (Coordinate)
Coordinates represent verified physical locations. They can have a nickname (key) or fall back to their realm name.

```python
from src.app.domain.models.resource_identity import LocalCoordinate, ResourceKey

# An Anchor (Root Cage) - Defaults to key "local"
anchor = LocalCoordinate("/srv/data/scans")
print(anchor.key) # Output: "local"

# A Specific Resource - Branded with a nickname
coord = LocalCoordinate("/srv/data/scans/01.csv", key=ResourceKey("scans"))
print(coord.key)  # Output: "scans"
```

---

## 2. ResourceCatalog (The Librarian)
The Catalog manages the mapping between "Nicknames" and "Physical Anchors."

```python
from src.app.domain.services.resource_identity.catalog import ResourceCatalog
from src.app.domain.models.resource_identity import LocalCoordinate

catalog = ResourceCatalog()

# 1. Register a Boundary (Security Guard) for the protocol
# catalog.register("posix", PosixResourceBoundary())

# 2. Add an Anchor (Nickname -> Physical Root)
# The key is derived from the nickname "scans"
catalog.add_anchor("scans", LocalCoordinate("/srv/data/scans"))

# 3. Resolve an Address
address = VirtualAddress("registry://scans/report.pdf")
coordinate = catalog.resolve(address)

print(coordinate.raw_value) # Output: "/srv/data/scans/report.pdf" (if resolved by boundary)
```

---

## 3. ResourceBoundary (The Gatekeeper)
Boundaries are implemented in the Infrastructure layer to perform security "math."

```python
from src.app.ports.input.resource_boundary import ResourceBoundary
from src.app.domain.models.resource_identity import Address, Coordinate, LocalCoordinate

class PosixResourceBoundary(ResourceBoundary):
    def resolve(self, address: Address, anchor: Coordinate) -> Coordinate:
        # 1. Get the path remainder from the address (e.g., "report.pdf")
        remainder = address.parsed.path.lstrip("/")
        
        # 2. Join with the anchor path ("/srv/data/scans")
        final_path = os.path.join(anchor.raw_value, remainder)
        
        # 3. Security Check (Simplified)
        if not final_path.startswith(anchor.raw_value):
            raise PermissionError("Directory Traversal Detected!")
            
        # 4. Return a branded Coordinate
        return LocalCoordinate(path=final_path, key=address.key)

    def is_safe(self, resource: Coordinate, anchor: Coordinate) -> bool:
        return resource.raw_value.startswith(anchor.raw_value)
```

---

## 4. The Promotion Lifecycle
How a string becomes a safe, usable stream location.

```python
# 1. Input: raw string
uri = "registry://scans/data.csv"

# 2. Classification: Factory turns string into Address
address = factory.build(uri) # Returns VirtualAddress

# 3. Resolution: Catalog turns Address into Coordinate
coordinate = catalog.resolve(address) # Returns LocalCoordinate

# 4. Execution: Adapter consumes the Coordinate
with PosixFileAdapter(coordinate) as stream:
    data = stream.read()
```
