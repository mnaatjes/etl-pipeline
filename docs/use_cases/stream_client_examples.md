# StreamClient Use-Case Examples

This document provides practical examples of using the `StreamClient` facade for standard data movement and manual processor integration. Note: These examples do not use the upcoming Pipeline DSL.

---

## 1. Basic Read from HTTP and Write to POSIX

This is the most common use case: pulling data from a remote URL and persisting it to the local filesystem.

```python
from src.app import StreamClient

client = StreamClient()

# 1. Open handles for Source and Sink
# Source: Remote HTTP Resource
# Sink: Local POSIX File (as_sink=True triggers write mode)
source_uri = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
sink_uri = "file://tests/data/tmp/words_download.txt"

with client.get_handle(source_uri) as source, \
     client.get_handle(sink_uri, as_sink=True) as sink:
    
    # 2. Iterate over packets from the source
    for packet in source.read():
        # 3. Write packet payload to the sink
        sink.write(packet)
```

---

## 2. Using the Resource Catalog (Logical URIs)

The framework allows you to define "anchors" for cleaner, location-agnostic code.

```python
client = StreamClient()

# 1. Register a physical directory under a logical key
client.add_resource(
    key="logs",
    protocol="posix",
    anchor="/var/log/myapp"
)

# 2. Access via logical URI (posix://logs/...)
# This resolves to /var/log/myapp/system.log
with client.get_handle("posix://logs/system.log", as_sink=True) as log_file:
    client.write("posix://logs/system.log", b"System initialized.")
```

---

## 3. Manual Processor Integration (The Generator Loop)

Before the Pipeline DSL is finalized, you can apply processors manually within the `get_handle` context. This demonstrates the "Manual Mechanism" the Pipeline DSL will eventually abstract.

```python
from src.infrastructure.processors.checksum import ChecksumProcessor

client = StreamClient()
hasher = ChecksumProcessor(algorithm="sha256")

source_uri = "https://example.com/data.bin"
sink_uri = "file://tests/data/tmp/data.bin.sha256"

with client.get_handle(source_uri) as source, \
     client.get_handle(sink_uri, as_sink=True) as sink:
    
    # Processors can be applied in the loop
    for packet in source.read():
        # 1. Transform/Process the packet
        processed_packets = hasher.process(packet)
        
        # 2. Write the resulting packets (processors return iterators)
        for p in processed_packets:
            sink.write(p)
    
    # 3. Finalize: Some processors need a flush signal at the end
    for final_packet in hasher.flush():
        sink.write(final_packet)
```

---

## 4. Introspection and Capabilities

You can ask a handle what it is capable of before performing operations.

```python
handle = client.get_handle("https://example.com/bigfile.zip")

# Check if the adapter supports random access (seeking)
if handle.capacity.can_seek:
    print("This resource supports random access!")
else:
    print("This is a sequential stream (like most network resources).")

# Check if it is a network resource
if handle.capacity.is_network:
    print("Warning: Latency may vary.")
```
