#
from enum import StrEnum
class HttpReadMode(StrEnum):
    """
    Defines the iteration strategy used by the HttpStream adapter.
    
    This setting determines how the underlying network response is sliced 
    into Envelope payloads.
    """

    BYTES = "bytes"
    """
    Implements: httpx.Response.iter_bytes(chunk_size)
    - Returns: Raw binary chunks.
    - Use Case: Default; ideal for general binary data, images, or large blobs.
    - Yields: Envelope(completeness=PARTIAL, regime=BYTES)
    """

    LINES = "lines"
    """
    Implements: httpx.Response.iter_lines()
    - Returns: UTF-8 decoded strings (line by line).
    - Use Case: Structured text like CSV, JSONL, or log files.
    - Yields: Envelope(completeness=COMPLETE, regime=BYTES)
    """

    TEXT = "text"
    """
    Implements: httpx.Response.iter_text(chunk_size)
    - Returns: Decoded strings (not necessarily split by line).
    - Use Case: Processing massive text bodies where line endings don't matter.
    - Yields: Envelope(completeness=PARTIAL, regime=BYTES)
    """

    RAW = "raw"
    """
    Implements: httpx.Response.iter_raw()
    - Returns: Bytes directly from the socket (no automatic decompression).
    - Use Case: High-performance mirroring or manual middleware decompression (Gzip/Zstd).
    - Yields: Envelope(completeness=PARTIAL, regime=BYTES)
    """