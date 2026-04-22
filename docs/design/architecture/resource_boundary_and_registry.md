# Resource Boundary & Registry Architecture

This document outlines the architectural decisions regarding the naming of restricted execution environments, the implementation of a universal registry system, and the use of strong typing for resource validation.

## 1. The "Sandbox" Naming & The Parent
To align with industry standards and avoid the informal connotations of "Sandbox," the system uses the concept of a **Boundary**. A boundary defines a restricted execution environment where processes are caged to prevent unauthorized system access.

*   **Parent:** `ResourceBoundary` (The abstract definition of "staying within limits").
*   **Realm-Specific Children:** `LocalResourceBoundary`, `NetworkResourceBoundary`, etc.

**Why this name?** It implies a hard limit. A boundary defines where operations must stop, providing a secure cage for protected resources.

## 2. The Universal Registry (`registry://`)
The `registry://` prefix is **Adapter Agnostic**, allowing the system to resolve resources without the caller needing to know the underlying storage mechanism.

### The Workflow:
1.  **The User:** Requests a resource, e.g., `registry://scans/001.xml`.
2.  **The ResourceFactory:** Acts as the "Traffic Controller." It identifies the `registry://` prefix and promotes it to a `VirtualAddress`.
3.  **The Catalog:** A global map that identifies the resource: `scans` -> `{protocol: "posix", anchor: "/srv/data/scans"}`.
4.  **The Resolution:** The Catalog invokes the appropriate `ResourceBoundary` (e.g., `PosixResourceBoundary`) to handle the resolution and enforcement.

## 3. Strong Typing: Address and Coordinate
Using specialized classes instead of raw strings prevents developer confusion and enables static analysis enforcement.

| Class | Type | Definition |
| :--- | :--- | :--- |
| `Address` | `Intent` | Any URI representing a requested resource. Untrusted. |
| `Coordinate` | `Reality` | A resource that has successfully passed the Boundary check. Trusted. |

### The Enforcement Rules:
*   **Logical:** If you have an `Address`, you **must** call the `ResourceManager` to resolve it. It cannot be passed directly to an Adapter.
*   **Physical:** If you have a `Coordinate`, the "Security Guard" (Boundary) has already verified it. Adapters only accept this type.

## 4. Registry Abstraction (The "Input Port")
In Hexagonal Architecture, the Registry is a Service that feeds into the Input Port (the Manager).

*   `src/app/ports/input/resource_boundaries/`: The refined interfaces for security enforcement.
*   `src/app/domain/services/resource_identity/`: The domain services for classification and resolution.

## 5. Execution Lifecycle

| Stage | Data Form | Type Label | Action |
| :--- | :--- | :--- | :--- |
| **Request** | `"registry://scans/file.xml"` | `Address` | Entered into `ResourceManager`. |
| **Lookup** | `scans` | `ResourceKey` | Queried in the `ResourceCatalog`. |
| **Boundary** | `ResourceBoundary` | Logic | Math: `Anchor + Subpath`. |
| **Resolved** | `/srv/data/scans/file.xml` | `Coordinate` | The "Secure" output of the Boundary. |
| **Execution** | `DataStream` | Adapter | Opens the `Coordinate`. |

## 6. The Registry & Catalog (The Manager)
The Registry acts as the source of truth and the manager. It doesn't perform the heavy lifting; instead, it knows which "tools" are available and who is allowed to use them.

*   **Role:** Inventory and Authorization.
*   **Responsibilities:**
    *   Mapping specific keys or types to their implementations.
    *   Managing the lifecycle of components.
    *   Deciding which "Worker" (Boundary) is assigned to a specific task.

## 7. The Boundary (The Worker)
The Boundary is a controlled execution environment. It is "dumb" in the sense that it doesn't decide what to run; it simply executes whatever the Manager gives it, within strict limits.

*   **Role:** Isolation and Execution.
*   **Responsibilities:**
    *   Providing a "clean room" where code can run without side effects leaking.
    *   Handling the low-level resource validation (POSIX paths, URL hosts, etc.).

## 8. Summary of the Strategy
1.  **Address:** "I want `registry://scans/data.csv`." (Intent).
2.  **Catalog:** "Key `scans` is a POSIX type at `/srv/data`." (Metadata).
3.  **Boundary:** Resolves to `/srv/data/scans/data.csv`. (Math & Security).
4.  **Coordinate:** The "Stamped" and verified reality.
5.  **Adapter:** Receives a `Coordinate` and performs the `open()` operation.
