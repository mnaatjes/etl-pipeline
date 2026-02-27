# src/infrastructure/streams/http/settings.py
from dataclasses import dataclass
from src.app.ports.settings import StreamContract

@dataclass(frozen=True)
class HttpSettings(StreamContract):
    # --- Mandatory Contract ---
    chunk_size:int = 1024
    use_lines:bool = False

    # --- Specific to HTTP Streams ---
    retries:int = 3
    timeout: float = 10.0
