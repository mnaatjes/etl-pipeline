#
from enum import StrEnum
class HttpReadMode(StrEnum):
    """
    Defines the iteration strategy used by the HttpStream adapter.
    
    This setting determines how the underlying network response is sliced 
    into Packet payloads.
    """

    BYTES = "bytes"
    """
    Implements: httpx.Response.iter_bytes(chunk_size)
    - Returns: Raw binary chunks.
    - Use Case: Default; ideal for general binary data, images, or large blobs.
    - Yields: Packet(completeness=PARTIAL, subject=BYTES)
    """

    LINES = "lines"
    """
    Implements: httpx.Response.iter_lines()
    - Returns: UTF-8 decoded strings (line by line).
    - Use Case: Structured text like CSV, JSONL, or log files.
    - Yields: Packet(completeness=COMPLETE, subject=BYTES)
    """

    TEXT = "text"
    """
    Implements: httpx.Response.iter_text(chunk_size)
    - Returns: Decoded strings (not necessarily split by line).
    - Use Case: Processing massive text bodies where line endings don't matter.
    - Yields: Packet(completeness=PARTIAL, subject=BYTES)
    """

    RAW = "raw"
    """
    Implements: httpx.Response.iter_raw()
    - Returns: Bytes directly from the socket (no automatic decompression).
    - Use Case: High-performance mirroring or manual middleware decompression (Gzip/Zstd).
    - Yields: Packet(completeness=PARTIAL, subject=BYTES)
    """