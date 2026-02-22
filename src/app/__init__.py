# /src/app/__init__.py

from . import ports
from . import pipelines
from . import middleware  # This is the directory of implementations

# --- Expose Ports (Abstracts) ---
from .ports.datastream import DataStream
from .ports.policy import BasePolicy
from .pipelines.base import Pipeline # FIX: Add the dot before pipelines

# Base Middleware Ports
from .ports.middleware import (
    ByteMiddleware,
    ObjectMiddleware
)

__all__ = [
    "ports",
    "pipelines",
    "middleware",      # The implementation sub-package
    "DataStream",
    "BasePolicy",
    "ByteMiddleware",  # The abstract interface
    "ObjectMiddleware",  # The abstract interface
    "Pipeline"
]