# Pipeline Telemetry & Progress Tracking

For 200GB+ files, visual feedback is essential to monitor throughput and ensure the process hasn't hung.

## ProgressTracker Middleware
Uses `tqdm` to track row processing speed.

```python
from tqdm import tqdm
from src.app import BaseMiddleware

class ProgressTracker(BaseMiddleware):
    def __init__(self, total_expected_bytes: int = None, unit: str = "rows"):
        self.pbar = tqdm(
            total=total_expected_bytes, 
            unit=unit, 
            unit_scale=True,
            desc="Processing Pipeline"
        )

    def __call__(self, item: Any) -> Any:
        count = len(item) if isinstance(item, list) else 1
        self.pbar.update(count)
        return item

    def close(self):
        self.pbar.close()
```

## ByteCounter (Download Speed)
Placed at the top of the processor list to track raw MB/s.

```python
class ByteCounter(BaseMiddleware):
    def __init__(self):
        self.pbar = tqdm(unit='B', unit_scale=True, unit_divisor=1024, desc="Download Speed")

    def __call__(self, item: bytes) -> bytes:
        if isinstance(item, bytes):
            self.pbar.update(len(item))
        return item
```

## Observable Pipeline Assembly

```python
pipeline = app.Pipeline(
    source=infra.RemoteHttpStream(url=big_url, chunk_size=65536),
    sink=infra.ParquetStreamSink(path=Path("output.parquet"), schema=schema),
    processors=[
        app.middleware.telemetry.ByteCounter(),     # Tracks MB/s from HTTP
        app.middleware.convert.GzipStreamDecoder(), # Decompress
        app.middleware.convert.LineBuffer(),        # Bytes -> List[str]
        app.middleware.convert.JsonLoader(),        # List[str] -> List[dict]
        app.middleware.telemetry.ProgressTracker(unit="rows"), # Tracks Row/s
        app.middleware.logic.PropertyExtractor(keys=["id", "val"]),
    ]
)
```

## Cleanup
Ensure `Pipeline.run` closes all middlewares to finalize progress bars cleanly:

```python
def run(self):
    try:
        with self.source as src, self.sink as snk:
            # ... loop logic ...
    finally:
        for p in self.processors:
            if hasattr(p, 'close'):
                p.close()
```
