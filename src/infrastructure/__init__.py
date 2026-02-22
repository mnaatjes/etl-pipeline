# src/infrastructure/__init__.py

# Use explicit relatives to avoid pytest path resolution issues
from .registry import StreamRegistry, ProtocolRegistration
from . import streams
from . import policies

# Optional: Promote most common implementations for easier access
from .streams.http import RemoteHttpStream
from .streams.local import LocalFileStream
from .streams.db_table import DbTableStream
from .policies.local import LocalFilePolicy

__all__ = [
    "StreamRegistry",
    "ProtocolRegistration",
    "streams",      # Allows: from src.infrastructure import streams
    "policies",     # Allows: from src.infrastructure import policies
    "RemoteHttpStream",
    "LocalFileStream",
    "DbTableStream",
    "LocalFilePolicy"
]