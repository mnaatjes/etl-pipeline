# Specialized Pipeline Components

Implementation details for handling high-volume, streaming data.

## GzipStreamMiddleware
Uses `zlib.decompressobj` for stateful decompression of byte chunks.

```python
import zlib
from src.app import ByteMiddleware

class GzipStreamMiddleware(ByteMiddleware):
    def __init__(self):
        # 16 + MAX_WBITS tells zlib to expect a gzip header
        self._decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)

    def process(self, chunk: bytes) -> bytes:
        return self._decompressor.decompress(chunk)
```

## LineBuffer Middleware (for JSONL)
Buffers partial lines and yields only complete JSON strings.

```python
class LineBuffer(ByteMiddleware):
    def __init__(self):
        self._buffer = bytearray()

    def process(self, chunk: bytes) -> List[str]:
        self._buffer.extend(chunk)
        lines = []
        if b'
' in self._buffer:
            parts = self._buffer.split(b'
')
            self._buffer = parts.pop() 
            for p in parts:
                if p:
                    lines.append(p.decode('utf-8'))
        return lines
```

## ParquetStreamSink
Collects rows into memory-efficient blocks (Row Groups) before flushing them using `pyarrow`.

```python
import pyarrow as pa
import pyarrow.parquet as pq

class ParquetStreamSink(DataStream):
    def __init__(self, path: Path, schema: pa.Schema, chunk_size: int = 10000):
        super().__init__(str(path), chunk_size=chunk_size, as_sink=True)
        self.path = path
        self.schema = schema
        self._buffer = []
        self._writer = None

    def _flush(self):
        if not self._buffer: return
        table = pa.Table.from_pylist(self._buffer, schema=self.schema)
        self._writer.write_table(table)
        self._buffer = []

    def write(self, row: dict):
        self._buffer.append(row)
        if len(self._buffer) >= self._chunk_size:
            self._flush()
```

## 1-to-Many Pipeline Logic
To support middlewares that return multiple items (like `LineBuffer`), `Pipeline.run` should be updated:

```python
def run(self):
    with self.source as src, self.sink as snk:
        for chunk in src.read():
            items = [chunk] 
            for process in self.processors:
                next_items = []
                for item in items:
                    result = process(item)
                    if result is None: continue
                    if isinstance(result, list):
                        next_items.extend(result)
                    else:
                        next_items.append(result)
                items = next_items
            for item in items:
                snk.write(item)
```
