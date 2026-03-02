# Resource Boundary & Registry Architecture

This document outlines the architectural decisions regarding the naming of restricted execution environments, the implementation of a universal registry system, and the use of strong typing for path validation.

## 1. The "Sandbox" Naming & The Parent
To align with industry standards and avoid the informal connotations of "Sandbox," the system uses the concept of a **Boundary**. A boundary defines a restricted execution environment where processes are caged to prevent unauthorized system access.

*   **Parent:** `PathBoundary` (The abstract definition of "staying within limits").
*   **Child:** `PosixPathBoundary` (The Linux-specific implementation for this environment).

**Why this name?** It implies a hard limit. A boundary defines where operations must stop, providing a "PathVault" for protected resources.

## 2. The Universal Registry (`registry://`)
The `registry://` prefix is **Adapter Agnostic**, allowing the system to resolve resources without the caller needing to know the underlying storage mechanism.

### The Workflow:
1.  **The User:** Requests a resource, e.g., `registry://scans/001.xml`.
2.  **The StreamManager:** Acts as the "Traffic Controller." It identifies the `registry://` prefix.
3.  **The Registry:** A global map (Catalog) that identifies the resource: `scans` -> `{type: "posix", anchor: "/srv/data/scans"}`.
4.  **The Resolution:** Since the type is `posix`, the Manager invokes `PosixFilePolicy` to handle the resolution and enforcement.
    *   *Note:* If the entry was `registry://weather_api`, the Registry might return `{type: "http", url: "https://api.weather.com"}`, triggering the `HttpPolicy`.

## 3. NewTypes: The "Branding" of Strings
Using `NewType` creates a unique identity for primitive types (like strings), preventing developer confusion and enabling static analysis enforcement.

**Placement:** `src/app/domain/models/types.py`

| NewType | Base Type | Definition |
| :--- | :--- | :--- |
| `LogicalURI` | `str` | Any string starting with `registry://` or a scheme. Untrusted. |
| `ResourceKey` | `str` | The "Alias" or identifier (e.g., `scans`, `weather_api`). |
| `ValidatedPath` | `pathlib.Path` | A Path object that has successfully passed the Boundary check. |

### The Enforcement Rules:
*   **Logical:** If you have a `LogicalURI`, you **must** call a Policy to resolve it. It cannot be passed directly to an Adapter.
*   **Physical:** If you have a `ValidatedPath`, the "Security Guard" (Boundary) has already verified it. Adapters only accept this type.

## 4. Registry Abstraction (The "Input Port")
In Hexagonal Architecture, the Registry is a Service that feeds into the Input Port (the Manager).

**Proposed File Placement:**
*   `src/app/ports/input/catalog.py`: The Interface for the Registry.
*   `src/app/domain/services/path_boundary.py`: The logic for "Chroot-lite" enforcement.

### Implementation Mapping:
| File | Role | Type | Logic |
| :--- | :--- | :--- | :--- |
| `catalog.py` | The Librarian | Concrete | A simple dict/map. It just looks up keys and finds the metadata (type, anchor, etc.). |
| `path_boundary.py` | The Guard (Parent) | Abstract | Defines the interface: `resolve()` and `is_safe()`. Does NOT know about Linux. |
| `posix_sandbox.py` | The Guard (Child) | Concrete | Implements `PathBoundary`. Knows about `pathlib`, `os.access`, and `/home/hp_prodesk`. |

## 5. Execution Lifecycle

| Stage | Data Form | Type Label | Action |
| :--- | :--- | :--- | :--- |
| **Request** | `"registry://scans/file.xml"` | `LogicalURI` | Entered into `StreamManager`. |
| **Lookup** | `scans` | `ResourceKey` | Queried in the `TypedRegistry`. |
| **Boundary** | `PosixPathBoundary` | Logic | Math: `Anchor + Subpath`. |
| **Resolved** | `/srv/data/scans/file.xml` | `ValidatedPath` | The "Secure" output of the Policy. |
| **Execution** | `PosixFileStream` | Adapter | Opens the `ValidatedPath`. |

## 6. The Registry (The Manager)
The Registry acts as the source of truth and the orchestrator. It doesn't perform the heavy lifting; instead, it knows which "tools" are available and who is allowed to use them.

*   **Role:** Inventory and Authorization.
*   **Responsibilities:**
    *   Mapping specific keys or types to their implementations (e.g., mapping `DataStream` to `S3Adapter`).
    *   Managing the lifecycle of components.
    *   Deciding which "Worker" (Sandbox) is assigned to a specific task.
*   **Implementation:** `src/app/registry/streams.py`.

## 7. The Sandbox (The Worker)
The Sandbox is a controlled execution environment. It is "dumb" in the sense that it doesn't decide what to run; it simply executes whatever the Registry gives it, within strict boundaries.

*   **Role:** Isolation and Execution.
*   **Responsibilities:**
    *   Providing a "clean room" where code can run without side effects leaking to the rest of the app.
    *   Handling the low-level resource cleanup (POSIX files, memory, etc.).
    *   Executing the logic defined by the Use Case.
*   **Implementation:** Often implemented within `src/app/use_cases/manager.py` or a dedicated infrastructure layer that wraps the adapters.

## 8. The Relationship: Interaction Workflow
The "Manager-Worker" dynamic ensures that the Sandbox never has to ask "What should I do?" and the Registry never has to ask "How do I write to a file?"

*   **The TypedRegistry (The Manager):** This is a global "Catalog." It is a simple mapping of `Key` -> `Metadata`. It doesn't know how to check a path; it only knows which "Worker" to call.
*   **The Sandbox/Boundary (The Worker):** This is the specialized logic. A `PosixSandbox` knows how to do octal math and check for `/etc` escapes. An `S3Sandbox` would know how to check bucket names and IAM prefixes.
*   **Centralization:** A single Registry holds them all. When it sees an entry marked `type: "posix"`, it hands the task to the `PosixSandbox`. If it sees `type: "s3"`, it hands it to a different sandbox.

### Interaction Steps:
1.  **Request:** A request hits the `stream_client.py`.
2.  **Lookup (Manager):** The Registry looks up the correct Port/Adapter and Policy required for that request.
3.  **Deployment:** The Registry "hands" these components to the Sandbox.
4.  **Execution (Worker):** The Sandbox executes the task using the provided tools. If the task crashes or leaks memory, only that Sandbox is affected—the Registry remains safe.

### Key Benefits:
| Benefit | Description |
| :--- | :--- |
| **Security** | The Registry can vet code before letting the Sandbox execute it. |
| **Testability** | You can give the Sandbox a "Mock Registry" to test logic in isolation. |
| **Scalability** | One Registry (Manager) can manage dozens of concurrent Sandboxes (Workers). |

## 9. Summary of the Strategy
1.  **LogicalURI:** "I want `local://scans/data.csv`." (String).
2.  **Catalog:** "Key `scans` is a POSIX type at `/srv/data`." (Metadata).
3.  **PosixSandbox:** Resolves to `/srv/data/scans/data.csv`. (Math).
4.  **ValidatedPath:** The Sandbox "stamps" the path as safe using `NewType` casting.
5.  **Adapter:** Receives a `ValidatedPath` and performs the `open()` operation.

## 10. The System Flow: From URI to Byte
The "Check-in" happens at the Manager, and the "Check-out" happens at the Adapter. The `registry://` prefix acts as the "Passport" that tells the system it needs to go through the Boundary.

| Stage | Component | Input Type | Action |
| :--- | :--- | :--- | :--- |
| **1. Entry** | `StreamManager` | `LogicalURI` | Receives `registry://scans/data.xml`. Identifies the registry scheme. |
| **2. Lookup** | `ResourceCatalog` | `ResourceKey` | Extracts `scans`. Finds metadata: `{type: "posix", anchor: "/srv/data"}`. |
| **3. Pivot** | `ResourceBoundary` | `LogicalURI` | The Security Gate. Joins Anchor + Sub-path and performs the "Chroot-lite" math. |
| **4. Exit** | `PosixFileStream` | `ValidatedPath` | Receives a "Stamp of Approval" (the Path object). Opens the file. |
