# Slalom: The Developer's Menu

Welcome to the **Slalom Framework**. This document is a high-level glossary and functional menu designed to help you navigate the system without needing to memorize the implementation details.

---

## 1. The Gateway: What can it do?

The `Gateway` is your primary interface. It hides all the "plumbing" (Dependency Injection, Session Context, etc.) and provides the "Golden Path" for data movement.

| Action | Method | Description |
| :--- | :--- | :--- |
| **Read Data** | `slalom.read(uri)` | Returns an iterator of `Packet` objects. |
| **Write Data** | `slalom.write(uri, data)` | Writes raw bytes or objects to a destination. |
| **Check Existence**| `slalom.exists(uri)` | Returns `True/False` without opening the stream. |
| **Discovery** | `slalom.list(uri)` | Lists all resources at a logical location (e.g., a directory). |
| **Metadata** | `slalom.info(uri)` | Returns a dictionary of size, permissions, and timestamps. |
| **CRUD: Delete** | `slalom.delete(uri)` | Removes a physical resource (with policy check). |
| **CRUD: Move** | `slalom.move(src, dst)` | Atomic rename or copy-and-delete across protocols. |
| **CRUD: Copy** | `slalom.copy(src, dst)` | Duplicates a resource to a new location. |
| **Orchestrate** | `slalom.pipeline(uri)` | Initiates the Fluent DSL for multi-step processing. |
| **Decorate** | `slalom.wrap(handle, [p])` | Wraps a single handle with standalone middleware. |

---

## 2. Resource Identity: How do I find my data?

Slalom uses a **Logical -> Physical** mapping system. You use "Nicknames" in your code, and the system resolves them to reality.

### The Five Realms
1.  **LOCAL:** Filesystems (`posix://`, `win://`).
2.  **NETWORK:** Remote APIs (`http://`, `https://`, `s3://`).
3.  **MEMORY:** In-process buffers (RAM).
4.  **SYNTHETIC:** Procedural generators (Mock data).
5.  **VIRTUAL:** Overlays and logical groupings.

### Common Tasks:
*   **Register an Anchor:** `slalom.add_resource("scans", "posix", "/srv/data/scans")`
*   **Access it:** Use `registry://scans/01.csv` (Resolves to `/srv/data/scans/01.csv`).
*   **Safety:** The `ResourceBoundary` ensures you can never use `../` to escape the anchor's root path.

---

## 3. Middleware Processors: How do I transform data?

Middleware in Slalom is **type-safe** and **context-aware**.

### Available Processors:
*   **`ChecksumProcessor`**: Calculates hashes (SHA256, MD5) on-the-fly. Location: `src/infrastructure/processors/checksum.py`.

### How to add your own Middleware:
1.  **Inherit** from `MiddlewareProcessor`.
2.  **Define Subjects:** Tell the system what you consume and produce (e.g., `BYTES` -> `JSON`).
3.  **Implement `process(packet)`**: Transform the payload and `yield` a spawned packet.
4.  **Implement `flush()`**: If you have a buffer, release the final data here.

---

## 4. Frequently Asked Questions (FAQ)

### "How do I build a Pipeline?"
Use the `pipeline()` DSL for sequential or broadcast operations:
```python
slalom.pipeline("registry://source/file.bin") \
      .through(ChecksumProcessor()) \
      .to("registry://backup/file.bin") \
      .run()
```

### "What is a Packet?"
A `Packet` is the "Smart Value Object" of the system. It contains:
*   **`payload`**: The actual data (bytes, dict, etc.).
*   **`context`**: The "Passport" (trace_id, origin URI, history).
*   **`identity`**: Lineage tracking (correlation_id, parent_id).

### "How do I change the chunk size for a single call?"
Every Gateway method accepts `**overrides`:
```python
for packet in slalom.read("http://...", chunk_size=8192, timeout=60.0):
    pass
```

### "Where is the 'Read Mode' warning coming from?"
The `PosixFileContract` triggers `[Warning] read_mode set to NONE` whenever you open a handle with `as_sink=True`. This is a safety feature that confirms the system is ignoring the "Read Strategy" because you are in a "Write Mode."
