# src/infrastructure/adapters/file/enums.py
from enum import StrEnum

class FileReadMode(StrEnum):
    """
    Defines the iteration strategy for the LocalFileStream.
    """
    BYTES = "bytes"
    """Returns raw binary chunks via file.read(chunk_size)."""

    LINES = "lines"
    """Returns text-decoded lines via file.readlines() or iteration."""

    TEXT = "text"
    """Returns decoded text chunks (ideal for massive single-line files)."""

    NONE = "none"
    """Explicitly for sinks (writing)"""