# Pipeline Orchestration Strategy

This document defines the conceptual and structural foundations for the StreamFlow pipeline system.

---

## 1. Conceptual Foundation: What IS a Pipeline?

Conceptually, a **Pipeline** is a pattern of "Data in Motion." In computer programming, it is a directed, sequential set of data-processing elements where the output of one stage is the input of the next.

Unlike a standard function call (which is discrete and "Cold"), a pipeline represents a **continuous flow**. It decouples the *generation* of data from its *transformation* and *storage*, allowing for memory-efficient processing of datasets that are too large to fit in RAM (e.g., 200GB logs or infinite sensor streams).

### The Anatomy of a Pipeline
A professional pipeline consists of five primary parts:
1.  **Source (Producer):** The origin of the data (e.g., a file, a database, an HTTP socket).
2.  **Packet (Unit of Work):** The "Smart Envelope" that wraps the raw data with metadata, trace IDs, and state labels.
3.  **Processors (Filters/Stages):** Independent logic units that transform, filter, or enrich the Packet.
4.  **Sink (Consumer):** The final destination where the data is persisted or consumed (e.g., a data warehouse, a terminal, a file).
5.  **Orchestrator (The Engine):** The "Control Plane" that connects the stages and manages the lifecycle (open, process, flush, close).

---

## 2. Pipeline Framework Requirements

A robust pipeline framework must provide more than just loops; it must manage the **complexities of the stream**.

### Core Capabilities
- **Type Safety & Handshakes:** The framework must ensure that Processor A's output is compatible with Processor B's input before execution.
- **Backpressure Management:** Handling scenarios where the Source is faster than the Sink, preventing memory overflows.
- **Error Handling & Dead Letter Queues:** Gracefully handling failures without crashing the entire stream.
- **Traceability:** Propagating a unique ID through every stage for auditing and debugging.
- **Resource Lifecycle:** Ensuring that file handles and network connections are closed even if an error occurs.

---

## 3. Architectural Placement: Where does the Pipeline live?

In a Hexagonal architecture, the Pipeline system occupies the **Infrastructure and Application Layers**, acting as the bridge between them.

### Relationship to the Framework
The Pipeline is a **High-Level Use Case** that coordinates multiple **Low-Level Ports** (DataStreams and Middleware).
- **StreamClient (Facade):** The entry point. It hides the complexity of the Orchestrator.
- **StreamManager (Orchestrator):** Resolves URIs into Handles.
- **PipelineOrchestrator (Runner):** Executes the data movement logic.

---

## 4. Architectural Patterns for Abstraction

When designing the pipeline "Mechanism," we can employ several patterns to keep it flexible:

### A. The Builder Pattern (Fluent Interface)
Provides a human-readable **Fluent DSL** (Domain Specific Language) for constructing complex flows.

#### What is a Fluent DSL?
A Fluent DSL is an API design pattern that allows code to be written as a "readable sentence" using **Method Chaining**. 

Instead of passing nested arguments into a constructor (which is "Inside-Out" and hard to read), a Fluent DSL allows you to chain commands from left to right.

**The Abstraction:**
*   **Imperative:** `run(sink, hash(gzip(source)))` — *Wait, where did it start?*
*   **Fluent DSL:** `source.gzip().hash().to(sink)` — *Clear, sequential, and readable.*

In StreamFlow, this pattern ensures that the user "describes" the pipeline topology without worrying about the underlying generator loops.

```python
# Best Practice: Decouple Definition from Execution
pipeline = (client.pipeline("http://source.data")
            .through(ChecksumProcessor())
            .through(GzipDecompressor())
            .to("file://output.bin"))

pipeline.run() # Execution only happens here
```

### B. The Composite Pattern (Sub-Pipelines)
Allows a pipeline to treat a "Chain of Processors" as a single processor.
```python
# A reusable "Cleanup" chain
cleansing_chain = Pipeline([StripWhitespace(), FilterProfanity()])

# Use the chain inside a larger pipeline
main_pipeline.through(cleansing_chain)
```

### C. The Strategy Pattern (Execution Engines)
Allows the same pipeline definition to run on different "Engines" (Local Threaded, Multiprocessing, or Distributed/Celery).
```python
# Run locally
pipeline.execute(engine="local")

# Run as a distributed background job
pipeline.execute(engine="distributed")
```

---

## 5. The User Facade: Accessing the Orchestration

The **`StreamClient`** should remain the "Single Point of Entry." Users should not have to instantiate the `PipelineOrchestrator` directly.

### Recommended Pattern: The Fluent Entry Point
```python
class StreamClient:
    def pipeline(self, source_uri: str) -> 'PipelineBuilder':
        """The entry point for complex data flows."""
        handle = self.get_handle(source_uri)
        return PipelineBuilder(handle, manager=self._manager)

class PipelineBuilder:
    def __init__(self, source, manager):
        self.source = source
        self.processors = []

    def through(self, processor: MiddlewareProcessor) -> 'PipelineBuilder':
        self.processors.append(processor)
        return self

    def to(self, sink_uri: str):
        """Finalizes the builder and returns a runnable Pipeline."""
        sink = self.manager.get_handle(sink_uri, as_sink=True)
        return PipelineOrchestrator(self.source, self.processors, sink)
```

---

## 6. The Core Challenge: The "Generator Pitfall"
In a Pipe-and-Filter architecture, middleware components are **Generators** (`Iterator[Packet]`). A manual implementation requires nested loops:

```python
# The "Pyramid of Doom" (Imperative Approach)
for packet in source.read():
    for item in processor_a.process(packet):
        for result in processor_b.process(item):
            sink.write(result.payload)
```

**Problems with this approach:**
- **Resource Leakage:** Forgetting to call `.close()`.
- **Buffer Stagnation:** Forgetting to call `.flush()`.
- **Complexity:** Adding stages makes the code unreadable.

---

## 7. The Professional Mechanism: The Orchestrator
The Orchestrator "pulls" data through the chain, managing the lifecycle and signals.

### Conceptual Implementation
```python
class PipelineOrchestrator:
    def run(self):
        with self.source as src, self.sink as snk:
            # Lifecycle: Open all stages
            for p in self.processors: p.open()
            
            try:
                for packet in src.read():
                    self._dispatch(packet, self.processors, snk)
                
                # Signal: STREAM_END (Flush buffers)
                for p in self.processors:
                    for final in p.flush():
                        snk.write(final)
            finally:
                for p in self.processors: p.close()
```

---

## 8. Abstracting Pipeline Flow Types

1.  **Linear Flow:** Strict `A -> B -> C` sequence.
2.  **Branching (Tee):** Split one source into multiple sinks.
3.  **Routing (Switch):** Send packets to different sinks based on their `subject`.
4.  **Aggregate (Batch):** Collect N packets before yielding 1 large packet.

---

## 9. Best Practices

- **Lazy Evaluation:** Never process data until the Sink asks for it.
- **Immutability:** Treat the `Packet` as immutable; use `.spawn()` to create derivatives.
- **Fail Fast:** Validate the entire chain's "Handshake" (Input/Output compatibility) before starting the stream.
- **Stateless Processors:** Whenever possible, keep processors stateless to allow for easier horizontal scaling.
