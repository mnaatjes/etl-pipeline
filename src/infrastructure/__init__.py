# src/infrastructure/__init__.py

from .registry import StreamRegistry, ProtocolRegistration
from .streams.http import RemoteHttpStream
from .streams.local import LocalFileStream
from .streams.db_table import DbTableStream
from .policies.local import LocalFilePolicy

__all__ = [
    # --- Stream Registry ---
    "StreamRegistry",
    # --- Datastream Implementations ---
    "RemoteHttpStream",
    "LocalFileStream",
    "DbTableStream",
    # --- Datastream Policies ---
    "LocalFilePolicy",
    # --- Schemas and Dataclasses ---
    "ProtocolRegistration"
]