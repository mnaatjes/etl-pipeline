# src/infrastructure/streams/local/settings.py
from dataclasses import dataclass
from src.app.ports.settings import StreamContract

@dataclass(frozen=True)
class LocalFileSettings(StreamContract):
    """
    Settings specifically for the Local File System adapter.
    Inherits 'chunk_size' and 'use_lines' from the StreamContract.
    """
    # Contract requirements
    chunk_size: int = 1024
    use_lines: bool = False

    # Local-specific knobs
    encoding: str = "utf-8"
    #auto_mkdir: bool = True     # Automatically create parent dirs on write?
    file_mode: str | None = None # Explicitly force 'rb' or 'wb' (Optional)