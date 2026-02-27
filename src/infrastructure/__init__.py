# src/infrastructure/__init__.py

# Use explicit relatives to avoid pytest path resolution issues
from .registry import StreamRegistry, ProtocolRegistration
from . import streams
from . import policies
from . import decorators

# Optional: Promote most common implementations for easier access
from .streams.http.adapter import RemoteHttpStream
from .streams.local.adapter import LocalFileStream
#from .streams.db.adapter import DbTableStream
from .policies.local import LocalFilePolicy
from .decorators.http_probe import HttpHeaderProbeDecorator

__all__ = [
    "StreamRegistry",
    "ProtocolRegistration",
    "HttpHeaderProbeDecorator",
    "streams",      # Allows: from src.infrastructure import streams
    "policies",     # Allows: from src.infrastructure import policies
    "decorators",
    "RemoteHttpStream",
    "LocalFileStream",
    #"DbTableStream",
    "LocalFilePolicy"
]