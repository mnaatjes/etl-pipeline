# Example Usage: Packet & Lineage

This guide explains how `Packet` objects (Smart Value Objects) carry data, context, and lineage throughout the system.

---

## 1. Anatomy of a Packet

A `Packet` is more than just data; it is a self-documenting object that knows its origin and history.

```python
from src.app.domain.models.packet import Packet

# Accessing packet components
packet = next(slalom.read("registry://source/file.txt"))

print(f"Data: {packet.payload}")
print(f"Trace ID: {packet.context.trace_id}")
print(f"Origin URI: {packet.context.origin_uri}")
```

---

## 2. Spawning & Lineage Tracking

When a processor transforms data, it should **spawn** a new packet. This preserves the original context while updating the lineage (correlation and parent IDs).

```python
# Inside a MiddlewareProcessor
def process(self, packet: Packet):
    new_payload = transform(packet.payload)
    
    # .spawn() creates a new packet linked to the original
    yield packet.spawn(payload=new_payload)

# Outside, you can inspect the lineage
new_packet = next(transformed_stream)
print(f"Is child of original: {new_packet.identity.parent_id == packet.identity.id}")
```

---

## 3. Completeness & Stream Flow

Packets also track their position within a stream and whether they represent the end of a sequence.

```python
for packet in slalom.read("registry://source/data.json"):
    if packet.completeness.is_last:
        print("Final packet received!")
    
    print(f"Byte Offset: {packet.flow.offset}")
```

---

## 4. Key Packet Components

| Component | Class | Description |
| :--- | :--- | :--- |
| **Payload** | `Any` | The actual data (bytes, dict, etc.). |
| **Context** | `SessionContext` | The "Passport" (trace_id, origin, overrides). |
| **Identity** | `PacketIdentity` | Lineage tracking (id, parent_id, correlation_id). |
| **Flow** | `PacketFlow` | Stream metadata (offset, chunk_index). |
| **Completeness**| `PacketCompleteness`| Sequence status (is_last). |
