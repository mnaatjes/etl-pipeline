# Smart Gateway Strategy

This document outlines the architectural roadmap for evolving the `StreamClient` and `StreamManager` into a "Smart Gateway."

## 1. Core Vision
A Smart Gateway doesn't just pass strings to adapters; it understands the **State** of the application and the **Capabilities** of the underlying infrastructure to provide a safer, more intuitive developer experience.

## 2. Planned Enhancements

### A. Catalog-Aware Resolution (Active Phase)
The Gateway should recognize registered protocols (e.g., `posix://`, `s3://`) as valid logical schemes.
- **Benefit:** Allows intuitive URIs like `posix://data/file.txt` to resolve via the Catalog without forcing the `registry://` prefix.

### B. Capability Discovery
The Gateway should return metadata about what a stream *can* do before the user attempts an operation.
- **Implementation:** Return a `StreamHandle` object containing:
    - `can_seek`: Boolean (True for local files, False for some HTTP streams).
    - `is_writeable`: Boolean (Based on `as_sink` and adapter support).
    - `media_type`: Inferred MIME type or schema type.

### C. Context & Trace Injection
Every stream opened via the Gateway should automatically inherit the application's telemetry context.
- **Implementation:** The Gateway injects a `PipelineContext` (TraceID, SpanID) into the `Packet` lifecycle.

### D. Permission Pre-flighting (Early Error Detection)
Instead of waiting for a `write()` call to fail with an OS error, the Gateway should check access rights during the `open()` phase.
- **Implementation:** Use `os.access` for POSIX or IAM check simulations for Cloud protocols.
- **Benefit:** Provides "Fail-Fast" behavior with descriptive error messages (e.g., "Write denied: Anchor '/srv/data' is Read-Only").

## 3. Comparison of Patterns

| Feature | Dumb Proxy (Legacy) | Smart Gateway (Future) |
| :--- | :--- | :--- |
| **URI Handling** | Hardcoded prefixes (`registry://`) | Contextual (Catalog-Aware) |
| **Error Handling** | Bubbles up raw OS exceptions | Wraps in Domain-Specific Advice |
| **Telemetry** | Manual injection per stream | Automatic Context Propagation |
| **Introspection** | "Try and see if it works" | "Ask what is possible" |
