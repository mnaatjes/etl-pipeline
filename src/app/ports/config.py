# src/app/ports/config.py

from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class AppConfig:
    """Settings for the Pipeline Engine Application"""
    env:Literal["dev", "prod", "test"] = "dev"
    log_level: Literal["INFO", "NONE"] = "INFO"
    chunk_size: int = 1024
    enable_telemetry: bool = True