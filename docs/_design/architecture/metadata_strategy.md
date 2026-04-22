# Metadata Management Strategy

The `metadata` dictionary in the `Envelope` is a flexible, pluggable container that allows Source adapters and Middleware to be descriptive without requiring changes to the central core.

---

## 1. Core Principles

### The "Add, Don't Replace" Rule
Treat the metadata dictionary as an append-only log. Middleware should update the dictionary, never overwrite it.

```python
# ✅ GOOD: Preserves existing metadata (source, index, etc.)
envelope.metadata["processed_at"] = time.time()

# ❌ BAD: Destroys all previous context
envelope.metadata = {"processed_at": time.time()} 
```

### Namespace Your Keys
As the pipeline grows, use namespaces to prevent key collisions between different middlewares.
*   `http_request_id`
*   `auth_user_id`
*   `sha256_checksum`

---

## 2. Defensive Implementation

### Safe Access with `.get()`
Since metadata is flexible, always use `.get()` to access keys. This prevents the pipeline from crashing if a specific chunk or source is missing a piece of information.

```python
# Defensive programming in a Sink or Middleware
chunk_idx = envelope.metadata.get("chunk_index", "unknown")
logger.info(f"Writing chunk {chunk_idx} to disk...")
```

### Memory and Performance: Shallow vs. Deep Copy
In Python, `new_metadata = envelope.metadata` creates a reference to the same dictionary.
*   **Performance**: Standard reference assignment is usually preferred for speed.
*   **Branching**: If you are branching your pipeline (sending the same chunk to two different destinations), use `envelope.metadata.copy()` to ensure one branch does not mutate metadata intended for the other.

---

## 3. Common Metadata Use Cases

| Use Case | Example Key | Purpose |
| :--- | :--- | :--- |
| **Tracking** | `chunk_index` | Sequencing and debugging failures. |
| **Attribution** | `source_url` | Identifying the origin of the data. |
| **Integrity** | `original_size` | Verifying that data hasn't drifted during processing. |
| **Diagnostics** | `arrival_time` | Calculating latency per middleware. |
| **Security** | `checksum` | Carrying a hash for end-to-end verification. |

---

## 4. Summary

The goal of this strategy is to keep the `Envelope` as a powerful "Passport" for the data. By following these rules, the metadata remains a reliable record of what has happened to the data as it travels from Source to Sink.
