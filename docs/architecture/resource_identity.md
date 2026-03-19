# As-Built: Resource Identity Subsystem

**Refactored: March 2026**

The Resource Identity subsystem is the security and classification backbone of the StreamFlow library. It provides a strictly typed, realm-aware framework for translating "User Intent" into "Physical Reality."

---

## 1. System Role & Philosophy

In a high-volume data pipeline, resource resolution is a primary security vulnerability. The Resource Identity subsystem mitigates this by enforcing a hard cleavage between:
1.  **Address (Intent)**: A logical reference that has not yet been vetted.
2.  **Coordinate (Reality)**: A physical location that has passed through a realm-specific **Boundary**.

**Core Mandate**: No Adapter (POSIX, HTTP, etc.) shall ever accept a raw string or an `Address`. They only accept `Coordinate` objects produced by an authorized `ResourceBoundary`.

---

## 2. The Taxonomy (Realms)

The subsystem is organized into five mutually exclusive **Realms**. Each realm has a corresponding `Address` and `Coordinate` pair.

| Realm | Description | Example Intent | Physical Reality |
| :--- | :--- | :--- | :--- |
| **Local** | OS-managed filesystems | `posix:///tmp/data.csv` | `/tmp/data.csv` |
| **Network** | Remote URLs/APIs | `https://api.com/v1` | `https://api.com/v1` |
| **Memory** | In-process buffers | `memory://cache/key` | `cache/key` |
| **Synthetic** | Procedural generators | `synthetic://faker/users` | `faker/users` |
| **Virtual** | Internal/Logical overlays | `registry://scans/01.csv` | `registry/scans/01.csv` |

---

## 3. The Genealogy (Class Hierarchy)

### Address Hierarchy (The Intent)
- `ResourceIdentity` (ABC)
    - `Address` (Base Intent)
        - `LocalAddress`: Filesystem-centric.
        - `NetworkAddress`: URL-centric.
        - `MemoryAddress`: RAM-centric.
        - `SyntheticAddress`: Generator-centric.
        - `VirtualAddress`: Logical-centric.

### Coordinate Hierarchy (The Reality)
- `ResourceIdentity` (ABC)
    - `Coordinate` (Base Reality)
        - `LocalCoordinate`: Verified Path.
        - `NetworkCoordinate`: Verified URL.
        - `MemoryCoordinate`: Verified Pointer/Key.
        - `SyntheticCoordinate`: Verified Generator ID.
        - `VirtualCoordinate`: Verified Overlay Path.

---

## 4. The Orchestration Lifecycle

The subsystem operates through a "Promotion" lifecycle managed by the `ResourceManager`.

1.  **Classify**: The `ResourceFactory` identifies the realm of a raw URI string and promotes it to a specialized `Address`.
2.  **Resolve**: If the intent is logical (e.g., `registry://`), the `ResourceCatalog` uses a `ResourceBoundary` to "join" the address with a physical **Anchor** (the security cage).
3.  **Validate**: The orchestrator runs a `StreamPolicy` check (Contextual Guard) against the resulting `Coordinate`.
4.  **Execute**: The final `Coordinate` is passed to the `DataStream` adapter.

---

## 5. Security: The Boundary Port

The `ResourceBoundary` is an **Input Port** refined by realm. It uses the **Template Method** pattern to enforce universal domain security rules while allowing infrastructure-specific path math.

- **Universal Rules**: Sanitization (stripping separators), Traversal protection (`..`), and Host/Protocol locking.
- **Infrastructure Rules**: Symlink resolution, OS-specific path joining (POSIX vs. Windows).

---

## 6. Links & Resources

- [Example Usages](../examples/resource_subsystem.md): Practical code samples.
- [Refinement Strategy](../architecture/resource_boundary_and_registry.md): The "Why" behind the design.
- [Status & Roadmap](../refactoring_stream_ports.md): Current completion status and next steps.
