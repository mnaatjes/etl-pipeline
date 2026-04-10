# Example Usage: Pipeline Fluent DSL

This guide demonstrates how to build and execute multi-step data processing workflows using the Slalom Pipeline DSL.

---

## 1. Basic Pipeline (Single Destination)

The Pipeline DSL allows you to chain transformations and destinations in a readable, fluent manner.

```python
from src.app import Gateway
from src.infrastructure.processors.checksum import ChecksumProcessor

slalom = Gateway()

# Define and run a simple pipeline
slalom.pipeline("registry://source/data.bin") \
      .through(ChecksumProcessor(algorithm="sha256")) \
      .to("registry://backup/data.bin") \
      .run()
```

---

## 2. Multi-Stage Transformations

You can chain multiple processors together. Data flows sequentially through each one.

```python
from src.infrastructure.processors.compression import CompressionProcessor
from src.infrastructure.processors.formats import JsonProcessor

slalom.pipeline("https://api.example.com/export.json") \
      .through(JsonProcessor()) \
      .through(CompressionProcessor(action="compress")) \
      .to("posix:///tmp/export.json.gz") \
      .run()
```

---

## 3. Advanced Configuration (Engines & Overrides)

Pipelines can be configured with specific execution engines or call-level overrides.

```python
# Pass overrides directly to the pipeline() entry point
slalom.pipeline(
    "registry://large-files/video.mp4",
    chunk_size=1024 * 1024,  # 1MB chunks
    timeout=300.0
) \
.to("s3://my-bucket/archive/video.mp4") \
.run(engine="local")  # Explicitly choose the 'local' execution engine
```

---

## 4. Understanding the Blueprint

When you build a pipeline, Slalom creates a `PipelineBlueprint`. This blueprint is a static model of the workflow that is then handed to a `PipelineEngine`.

| Method | Role |
| :--- | :--- |
| `pipeline(uri)` | The entry point. Creates the `PipelineBuilder` and sets the **Source**. |
| `.through(processor)` | Adds a **MiddlewareProcessor** stage to the blueprint. |
| `.to(uri)` | Adds a **Sink** (Destination) to the blueprint. |
| `.run(engine)` | Finalizes the blueprint and triggers the **PipelineRunner**. |
