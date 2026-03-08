# Middleware Processing Patterns

This document defines the core data transformation patterns used within the StreamFlow `MiddlewareProcessor` framework.

## 1. Pattern Overview Matrix

| Pattern | Name | Ratio | Responsibility | Example |
| :--- | :--- | :--- | :--- | :--- |
| **1:1** | **Transformer** | 1 In : 1 Out | Stateless mapping or filtering. | Uppercase, Encryption, Data Masking. |
| **N:1** | **Aggregator** | N In : 1 Out | Stateful accumulation of chunks into units. | JSON Stitching, IP Address Assembly. |
| **1:N** | **Decomposer** | 1 In : N Out | Exploding a single unit into multiple parts. | CSV Row Splitter, JSON Array Unnesting. |

---

## 2. The Transformer (1:1)
The simplest pattern. It receives a packet, transforms the payload, and yields a single derivative.

### Flow
`[Packet A] --> [Processor] --> [Packet A']`

### Implementation Strategy
Use this for validation or simple type conversion.

```python
class UppercaseTransformer(MiddlewareProcessor):
    def process(self, packet: Packet) -> Iterator[Packet]:
        # Simple 1:1 mapping
        new_payload = packet.payload.decode("utf-8").upper().encode("utf-8")
        yield packet.spawn(payload=new_payload)

    def flush(self): return iter([]) # No state to clear
```

---

## 3. The Aggregator (N:1)
A stateful pattern that "holds its breath." It collects partial chunks until a logical unit is complete.

### Flow
`[Chunk 1] --+`
`[Chunk 2] --|--> [Processor] --> [Complete Unit]`
`[Chunk 3] --+`

### Implementation Strategy
Requires an internal buffer. Must implement `flush()` to handle the end of the stream.

```python
class LineAggregator(MiddlewareProcessor):
    def __init__(self):
        self._buffer = []

    def process(self, packet: Packet) -> Iterator[Packet]:
        self._buffer.append(packet.payload)
        
        # Optional: "Live Flush" if a delimiter is found
        if b"\n" in packet.payload:
            yield from self.flush()

    def flush(self) -> Iterator[Packet]:
        if self._buffer:
            full_unit = b"".join(self._buffer)
            yield self._last_packet.spawn(payload=full_unit)
            self._buffer = []
```

---

## 4. The Decomposer (1:N)
The "Exploding" pattern. It takes a complex object and breaks it into smaller, specialized packets.

### Flow
`                       +--> [Field A]`
`[Complex Packet] --> [Processor] --|--> [Field B]`
`                       +--> [Field C]`

### Implementation Strategy
Used for normalization. Often changes the `PayloadSubject` for each yielded packet.

```python
class UserDecomposer(MiddlewareProcessor):
    def process(self, packet: Packet) -> Iterator[Packet]:
        user_dict = packet.payload # Assumes DICT subject
        
        # Yield Username as TEXT
        yield packet.spawn(payload=user_dict['name'], subject=PayloadSubject.BYTES)
        
        # Yield Metadata as JSON
        yield packet.spawn(payload=user_dict['meta'], subject=PayloadSubject.JSON)
```

---

## 5. Summary of Best Practices
1.  **Immutability**: Never modify the incoming packet. Always use `packet.spawn()`.
2.  **Lineage**: The `spawn()` method automatically preserves the `correlation_id` and `trace_id`.
3.  **Subject Awareness**: Always check `packet.subject` before processing to ensure compatibility.
