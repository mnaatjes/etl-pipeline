# Pipeline Workflow Mapping

To handle a `.json.gz` to `.parquet` workflow, the responsibilities are distributed across the pipeline components.

## Component Responsibilities

| Task | Component | Responsibility |
| :--- | :--- | :--- |
| **Download** | `source` (RemoteHttpStream) | Fetches raw compressed bytes from the URL. |
| **Decompress** | `middleware` (GzipDecoder) | Converts bytes (.gz) $ightarrow$ bytes (raw JSON). |
| **Parse JSON** | `middleware` (JsonLoader) | Converts bytes $ightarrow$ dict. |
| **Extract Keys** | `middleware` (KeyFilter) | Pulls specific pairs; returns a filtered dict. |
| **Write Parquet** | `sink` (LocalFileStream/ParquetSink) | Takes the final dict and appends it to a Parquet file. |

## The "Type-Change" Challenge

The Pipeline allows the `processed_chunk` to change types as it moves through the `processors` list. While powerful, this requires careful coordination:
- A `RemoteHttpStream` yields `bytes`.
- A `GzipDecoder` receives `bytes` and yields `bytes`.
- A `JsonLoader` receives `bytes` (or `str`) and yields a `dict`.
- A `KeyFilter` receives a `dict` and yields a filtered `dict`.

## Recommended Middleware Chain

To keep the system flexible, tasks should be broken into "Micro-Middlewares":

```python
pipeline = Pipeline(
    source=infra.RemoteHttpStream(url=gz_url),
    sink=infra.LocalFileStream(path="output.parquet"),
    processors=[
        app.middleware.convert.GzipDecompressor(), # bytes -> bytes
        app.middleware.convert.BytesToJson(),      # bytes -> dict
        app.middleware.logic.PropertyExtractor(keys=["id", "status"]), # dict -> dict
        app.middleware.metrics.RowCounter()        # side-effect
    ]
)
```

## Flexibility & Constraints
The pipeline assumes the `source.read()` yields processable pieces. If dealing with large non-newline-delimited JSON files, standard `json.loads` will fail on partial chunks, requiring streaming parsers or line-buffering strategies.
