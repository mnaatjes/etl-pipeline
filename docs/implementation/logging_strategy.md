# Logging Strategy (Future Enhancement)

This document outlines the architectural vision for introducing logging into the StreamFlow framework. Logging is a **Cross-Cutting Concern** that should be implemented with minimal impact on business logic.

## 1. Core Principles
- **Separation of Concerns:** The domain layer should not know about log files or standard output. It should only emit events.
- **Structured Logging:** We prefer key-value pairs (e.g., `{"event": "stream_opened", "uri": "..."}`) over raw text strings.
- **Leveled Logging:**
    - `DEBUG`: High-volume internal tracing (e.g., individual packet transfers).
    - `INFO`: Significant lifecycle events (e.g., Stream Opened, Pipeline Completed).
    - `WARNING`: Recoverable issues (e.g., Retry attempt on a network failure).
    - `ERROR`: Unrecoverable issues that require intervention.

## 2. The Python `logging` Module
Python's built-in `logging` module is powerful and hierarchical. We will use it as our "Infrastructure Adapter" for observability.

### Components:
1. **Logger:** The interface used by the code to emit logs.
2. **Handler:** Determines where the log goes (Console, File, Network).
3. **Formatter:** Determines the final string format (JSON, Text).

## 3. Architectural Integration

### A. The "Logger Per Module" Pattern
Every file in the `src/` directory should define its own logger. This allows us to mute or enable logs for specific components (e.g., "Mute HTTP logs but show POSIX logs").

```python
import logging
logger = logging.getLogger(__name__) # e.g., 'src.infrastructure.adapters.posix_file'

def open_stream(self):
    logger.info(f"Opening POSIX stream at {self.path}")
```

### B. The Gateway Integration
The `StreamManager` (The Smart Gateway) will be the primary source of truth for high-level lifecycle logging.
- **On `get_stream`:** Log the resolution path and the selected adapter.
- **On `Error`:** Use the `GatewayAdvisor` to log descriptive domain errors.

## 4. Why wait? (The Roadmap)
Logging adds complexity to tests and requires a "Global Configuration" strategy. By implementing it as a standalone feature, we can:
1. Ensure the core "Smart Gateway" logic is stable first.
2. Integrate it with the `PipelineContext` so that every log entry automatically includes the `trace_id`.

## 5. Summary: What you do in a feature
- **Don't use `print()`**: Use `logger.info()`.
- **Context is King**: Always include the resource key or URI in the log entry.
- **Fail Loudly**: Errors should be logged before being raised to the user.
