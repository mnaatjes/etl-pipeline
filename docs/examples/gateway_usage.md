# Gateway Usage Examples

The `Gateway` is the primary entry point for the Slalom framework. It abstracts the underlying orchestration of identity, session context, and stream management.

---

## 1. Basic Read and Write

The simplest way to interact with resources is using the `read()` and `write()` methods. These methods automatically handle session context and traceability.

```python
from src.app import Gateway

# 1. Initialize the Gateway
# You can optionally provide global configuration or a trace_id
slalom = Gateway(chunk_size=1024, trace_id="my-app-session")

# 2. Read Packets from a URI
# Each packet is a 'Smart Value Object' containing payload and context.
for packet in slalom.read("https://example.com/data.json"):
    print(f"[{packet.context.trace_id}] Payload: {packet.payload}")

# 3. Write Data to a URI
# The system automatically stamps the data with the gateway's context.
slalom.write("posix:///tmp/output.txt", b"Hello, Slalom!")
```

---

## 2. Advanced I/O with Smart Handles

For more control, such as introspection or explicit resource management, use `get_handle()`.

```python
# Request a Smart Handle
# 'as_sink=True' prepares the resource for writing.
# Overrides can be passed per-call.
handle = slalom.get_handle(
    "registry://scans/01.csv", 
    as_sink=False, 
    chunk_size=8192
)

# Use Introspection (Ask what is possible)
if handle.capacity.can_seek:
    print("This stream supports random access!")

# Use the handle as a Context Manager
with handle as stream:
    for packet in stream.read():
        # Process packets...
        pass
```

---

## 3. Resource Registration (Anchors)

Define "anchors" to create logical, location-agnostic URIs.

```python
# Register a physical directory under a logical key
# This maps 'registry://logs/...' to '/var/log/myapp/...'
slalom.add_resource(
    key="logs",
    protocol="posix",
    anchor="/var/log/myapp"
)

# Access via logical URI
# This resolves to /var/log/myapp/system.log
for packet in slalom.read("registry://logs/system.log"):
    print(packet.payload)
```

---

## 4. Standalone Middleware Decoration

You can wrap a `StreamHandle` with middleware processors outside of a full pipeline context.

```python
from src.infrastructure.processors.checksum import ChecksumProcessor

# 1. Initialize a Processor
hasher = ChecksumProcessor(algorithm="sha256")

# 2. Get a Handle and wrap it
raw_handle = slalom.get_handle("https://example.com/bigfile.zip")
secure_handle = slalom.wrap(raw_handle, [hasher])

# 3. Read through the transformation chain
with secure_handle as stream:
    for packet in stream.read():
        # Packets are processed as they are yielded
        pass

print(f"Final Hash: {hasher.get_hash()}")
```

---

## 5. Summary of Gateway Methods

| Method | Description |
| :--- | :--- |
| `read(uri, **overrides)` | Convenience iterator for reading `Packet` objects. |
| `write(uri, data, **overrides)` | Convenience method for writing data. |
| `get_handle(uri, as_sink, **overrides)` | Returns a `StreamHandle` for advanced operations. |
| `add_resource(key, protocol, anchor)` | Registers a logical anchor in the system. |
| `exists(uri)` | Checks for physical resource existence. |
| `wrap(handle, processors)` | Decorates a handle with middleware. |
| `pipeline(uri, **overrides)` | (Upcoming) Fluent DSL for multi-step processing. |
