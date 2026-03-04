# Middleware Strategy (v2.0.0)

This document defines the implementation standards for data transformation within the StreamFlow framework.

## 1. Architectural Philosophy: Pipe-and-Filter
StreamFlow treats data as a continuous stream of **Self-Aware Packets**. Middleware components act as "Filters" that can be chained together.

### The "Self-Governing" Principle
Each middleware is an independent unit. It is responsible for its own resource lifecycle (`open/close`) and must decide how to handle data based on the **Packet labels** (`subject`, `signal`, `completeness`).

---

## 2. The Middleware Contract
Every processor must implement the `MiddlewareProcessor` port. It relates to the `Packet` properties as follows:

| Packet Property | Middleware Responsibility |
| :--- | :--- |
| **`subject`** | **Verification:** Check `packet.subject == self.input_subject`. If incompatible, log/drop. |
| **`signal`** | **Orchestration:** Observe `STREAM_START` to init buffers and `STREAM_END` to trigger `flush()`. |
| **`context`** | **Observability:** Never drop the passport. Always use `packet.spawn()` to keep the `trace_id` alive. |
| **`identity`** | **Lineage:** Use `packet.spawn()` so the framework can link the child packet to its parent ID. |

---

## 3. Pattern Prototypes

### A. The Stateless Filter (1:1 or 1:0)
Used for validation, encryption, or simple field mapping.
```python
class TypeConverter(MiddlewareProcessor):
    @property
    def input_subject(self) -> PayloadType: return PayloadSubject.BYTES
    @property
    def output_subject(self) -> PayloadType: return PayloadSubject.TEXT

    def process(self, packet: Packet) -> Iterator[Packet]:
        # Logic: Convert bytes chunk to string
        try:
            text = packet.payload.decode("utf-8")
            yield packet.spawn(payload=text, subject=self.output_subject)
        except UnicodeDecodeError:
            return # Drop invalid packets
```

### B. The Exploding Filter (1:N)
Used for unnesting arrays or splitting lines into words.
```python
class WordSplitter(MiddlewareProcessor):
    def process(self, packet: Packet) -> Iterator[Packet]:
        words = packet.payload.split(" ")
        for word in words:
            # Identity.spawn() creates unique IDs for each word linked to the source packet
            yield packet.spawn(payload=word)
```

### C. The Aggregating Filter (N:1)
Used for batching, summing, or compression. Requires `flush()`.
```python
class BatchProcessor(MiddlewareProcessor):
    def __init__(self, batch_size: int = 100):
        self.buffer = []
        self.size = batch_size

    def process(self, packet: Packet) -> Iterator[Packet]:
        self.buffer.append(packet.payload)
        if len(self.buffer) >= self.size:
            yield from self.flush()

    def flush(self) -> Iterator[Packet]:
        if self.buffer:
            # Logic: Yield the batch as a single unit
            # Note: We'd ideally take context from the last packet in buffer
            result = list(self.buffer)
            self.buffer = []
            yield Packet(payload=result, ...)
```

---

## 4. Friction Analysis (Current System Gaps)

While the `Packet` and `StreamHandle` are robust, the following "Points of Friction" exist in the framework as of v2.0.0:

### Friction Point 1: The "Missing Link" (Chaining)
**Problem:** Currently, there is no **`Pipeline`** object. A user has to manually loop through `stream.read()` and pass results to `processor.process()`.
**Friction:** High boilerplate for the end user.
**Proposed Fix:** Implement a `Pipeline` or `Flow` model that allows `handle.pipe(ProcessorA).pipe(ProcessorB)`.

### Friction Point 2: Protocol Handshaking
**Problem:** The `subject` (e.g., `PayloadSubject.BYTES`) is currently a convention, not a hard enforcement.
**Friction:** If a user pipes a `JSON` processor directly into an image resizer, it will crash at runtime.
**Proposed Fix:** Add a `validate_chain()` method to the `StreamManager` that checks `output_subject == next.input_subject` before the stream opens.

### Friction Point 3: Error Propagation
**Problem:** If a processor fails deep in a chain, the `StreamHandle` might not know why, or worse, might leave the physical `DataStream` open.
**Friction:** Leakage of file descriptors and "vague" error messages.
**Proposed Fix:** Implement the **`GatewayAdvisor`** to map processor-level exceptions to specific packet IDs and trace IDs.

### Friction Point 4: Config Propagation
**Problem:** Middleware often needs its own settings (e.g., `batch_size`). Currently, `AppConfig` only targets `DataStreams`.
**Friction:** Passing settings to middleware is manual and inconsistent.
**Proposed Fix:** Extend the `SettingsResolver` to support `MiddlewareContract` hydration.
