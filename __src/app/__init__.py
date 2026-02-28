# /src/app/__init__.py

from . import ports
from . import jobs
from . import middleware  # This is the directory of implementations

# --- Expose Ports (Abstracts) ---
from .ports.datastream import DataStream
from .ports.decorator import Decorator
from .ports.policy import BasePolicy
from .jobs.base import Linear # FIX: Add the dot before pipelines
from .ports.config import AppConfig, Environment
from .ports.settings import StreamContract
from .bootstrap import Bootstrap

# Base Middleware Ports
from .ports.middleware import (
    BaseMiddleware,
    ByteMiddleware,
    ObjectMiddleware
)

# --- FASCADE ---
def build(env:Environment=Environment.DEV, **kwargs):
    """Entry Point for Bootstrapping the engine and returning the managing"""
    # Assemble Configuration Dataclass
    config = AppConfig(env=env, **kwargs)

    # Initiate Bootstrapper
    boot = Bootstrap(config)

    # Return Manager
    return boot.build_manager()


# --- Registry of Ports and Packages ---
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