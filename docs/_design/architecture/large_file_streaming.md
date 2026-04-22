# Streaming Architecture for Large Files (200GB+)

Handling 200GB+ files requires a streaming-first approach to avoid Out of Memory (OOM) errors. Standard Python processing, which might load a whole file into RAM, would fail.

## Memory Usage Comparison (200GB File)

| Component | "Standard" Way | "Streaming" Pipeline |
| :--- | :--- | :--- |
| **Source** | 200 GB (OOM) | 64 KB (Buffer) |
| **Middleware** | 400 GB (Decompressed OOM) | 128 KB (Uncompressed chunk) |
| **Sink** | 200 GB (Memory Table) | 50 MB (Buffered Row Group) |
| **Total RAM** | **Fail** | **~200 MB** |

## The Gzip "Concatenation" Problem

Gzip files are composed of compressed blocks. Standard `gzip.decompress()` requires the whole byte-string. For a pipeline, stateful decompression using `zlib.decompressobj` is required to handle chunks correctly.

## The "Incomplete JSON" Challenge

A 64KB chunk of decompressed bytes will likely end in the middle of a JSON line or object. Two primary strategies address this:

### 1. The "Buffer to Newline" Strategy (Fastest)
If the file is JSONL (JSON Lines), a middleware buffers trailing fragments and prepends them to the next chunk, only yielding complete lines.

### 2. The `ijson` Strategy (Most Flexible)
If the file is a giant JSON array `[...]`, `ijson` acts as a cursor that yields objects from a stream of bytes without needing the whole file.

## Linux Pro-Tips

### Pipe Performance
Decompressing 200GB while writing to an encrypted SSD will likely be the bottleneck. Utilizing `threading` or `multiprocessing` can allow decompression and writing to run on separate CPU cores.

### Resource Impact
- **Disk Space**: 0 bytes of extra disk space needed for the uncompressed version.
- **RAM**: Capped by the defined chunk size and row group buffer.
- **CPU**: This is the main bottleneck; expect high CPU usage during decompression and parsing.
