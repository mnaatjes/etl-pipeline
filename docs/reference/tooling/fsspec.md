---
id: REF-TOOL-FSSPEC
title: "fsspec (Filesystem Spec)"
status: stable
created_at: 2026-04-23
updated_at: 2026-04-23
component: core
type: "reference/tooling"
---

# fsspec (Filesystem Spec)

`fsspec` is a professional Python library that provides a unified, abstract interface to many different filesystems and storage backends. In Slalom, it serves as the "Identity Killer," replacing custom URI resolution logic with a standardized industry API.

## Core Concept: Protocol Transparency

The power of `fsspec` lies in its ability to treat any data source identically. Whether data is on your local hard drive, a web server, or an S3 bucket, the code you write to interact with it remains the same.

| URI Scheme | Backend | Required Driver |
| :--- | :--- | :--- |
| `file://` | Local Disk | (Built-in) |
| `https://` | Remote Web | `httpx` or `requests` |
| `s3://` | AWS S3 | `s3fs` |
| `memory://` | RAM | (Built-in) |

---

## Simple Python Examples

### 1. Opening a Local File
Instead of using `open()`, use `fsspec.open()`. This ensures that if you change the path to a URL later, your code doesn't break.

```python
import fsspec

# Opens a local file in binary read mode
with fsspec.open("file:///path/to/data.txt", mode="rb") as f:
    content = f.read()
    print(content)
```

### 2. Opening a Remote Resource
The syntax is identical to local I/O. `fsspec` handles the network handshake and streaming automatically.

```python
import fsspec

# Streams a remote file without downloading the whole thing at once
with fsspec.open("https://example.com/massive_data.csv", mode="rt") as f:
    for line in f:
        print(line)
```

### 3. Path Sandboxing (The "Anchor" Logic)
Slalom uses `fsspec`'s `DirFileSystem` to enforce physical jails (Anchors). This prevents a pipeline from accessing files outside a specific directory.

```python
from fsspec.implementations.local import LocalFileSystem
from fsspec.implementations.dirfs import DirFileSystem

# 1. Define the physical root (The Anchor)
local_fs = LocalFileSystem()
jail = DirFileSystem(path="/srv/data/scans/", fs=local_fs)

# 2. Access files relative to the jail
# This will physically open /srv/data/scans/01.csv
with jail.open("01.csv", mode="rb") as f:
    print(f.read())
```

### 4. Memory-Only Filesystem (Fast Testing)
Perfect for unit tests where you don't want to touch the disk.

```python
import fsspec

fs = fsspec.filesystem("memory")

with fs.open("test.bin", "wb") as f:
    f.write(b"hello slalom")

# The file exists only in RAM
print(fs.ls("/"))
```

---

## Why Slalom Uses fsspec
1. **Collapses Complexity:** Replaces ~1,500 lines of custom v0.9.0 identity code.
2. **Standardization:** It is the same engine used by `Pandas`, `Dask`, and `HuggingFace`.
3. **Lazy Loading:** Native support for streaming ensures Slalom stays "Lean" and memory-efficient.
