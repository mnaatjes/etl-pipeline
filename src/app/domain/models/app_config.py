# src/app/domain/models/app_config.py
from enum import Enum
from dataclasses import dataclass

class Environment(str, Enum):
    DEV = "DEV"
    PROD = "PROD"
    TEST = "TEST"

class LogLevel(str, Enum):
    INFO = "INFO"
    NONE = "NONE"

@dataclass(frozen=True)
class AppConfig:
    """Settings for the Pipeline Engine Application"""
    env:Environment = Environment.DEV
    log_level: LogLevel = LogLevel.INFO
    chunk_size: int = 1024
    enable_telemetry: bool = True