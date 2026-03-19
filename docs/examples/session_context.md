# Example Usage: Session Context & Traceability

This guide demonstrates how to use the `SessionManager` to maintain the "Passport" (Traceability + Settings) for data streams.

---

## 1. Building the Session Context (The Passport)

The `SessionManager` is responsible for generating the `SessionContext`. This object travels with every request to the `StreamManager`.

```python
from src.app.domain.services.session_context import SessionManager
from src.app.domain.models.session_context import TraceID

# 1. SETUP: Components are usually injected via a Container
manager = container.session_manager 

# 2. SESSION-LEVEL: Create a basic context for the current session
session_id = TraceID("user-session-123")
context = manager.build_context(session_trace=session_id)

# 3. METHOD-LEVEL: Override the Trace ID for a specific operation
# This is useful for debugging a single API call or job.
op_context = manager.build_context(
    session_trace=session_id,
    method_trace="job-01-processing"
)

# 4. CAPTURE OVERRIDES: Pass ephemeral settings for the stream
# These settings will override global defaults during I/O.
custom_context = manager.build_context(
    session_trace=session_id,
    chunk_size=4096,
    verify_ssl=False
)
```

---

## 2. Using the Context with StreamManager

The `SessionContext` is a mandatory argument for the `StreamManager`. It tells the system **Who/How** the resource is being accessed.

```python
from src.app.use_cases.manager import StreamManager

# 1. Provide the URI and the SessionContext
uri = "registry://scans/01.csv"
handle = stream_manager.get_handle(uri, session_context=custom_context)

# 2. The Waterfall Effect
# - Global settings (AppConfig) are loaded first.
# - 'chunk_size=4096' and 'verify_ssl=False' are merged in.
# - The resulting 'Dense Bag' is injected into the Adapter.
with handle as stream:
    for packet in stream.read():
        # Each packet now carries the 'job-01-processing' trace_id
        print(f"Trace: {packet.trace_id} | Data: {packet.payload}")
```

---

## 3. The Settings Waterfall (Visualized)

The `SessionManager` delegates the merging logic to the `SettingsResolver`.

| Tier | Source | Priority | Description |
| :--- | :--- | :--- | :--- |
| **Tier 1** | `AppConfig` | Baseline | Global defaults defined at startup. |
| **Tier 2** | `SessionContext` | Overrides | Per-request or per-session settings. |
| **Tier 3** | Adapter Defaults | Fallback | Defined in the infrastructure adapter class. |

---

## 4. Why Use SessionContext?

1.  **Observability:** Every log line and every data packet is stamped with a `trace_id` for end-to-end debugging.
2.  **Ephemerality:** Change settings (like timeouts or retry policies) for a single operation without modifying global state.
3.  **Decoupling:** The `StreamManager` doesn't need to know about "Users" or "Sessions"; it just knows it has a "Passport" with instructions.
