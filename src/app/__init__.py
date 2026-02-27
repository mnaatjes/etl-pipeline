# /src/app/__init__.py

from . import ports
from . import jobs
from . import middleware  # This is the directory of implementations

# --- Expose Ports (Abstracts) ---
from .ports.datastream import DataStream
from .ports.decorator import Decorator
from .ports.policy import BasePolicy
from .jobs.base import Linear # FIX: Add the dot before pipelines
from .ports.config import AppConfig
from .ports.settings import StreamContract

# Base Middleware Ports
from .ports.middleware import (
    BaseMiddleware,
    ByteMiddleware,
    ObjectMiddleware
)

__all__ = [
    # --- Major Packages ---
    "ports",
    "jobs",
    "middleware",
    # --- Configuration and Settings ---
    "StreamContract",
    "AppConfig",
    # --- Major Ports ---
    "DataStream",
    "BasePolicy",
    "Linear",
    "Decorator"
]