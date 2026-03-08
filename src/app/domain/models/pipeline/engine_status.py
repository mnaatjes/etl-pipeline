# src/app/domain/models/pipeline/engine_status.py
from enum import StrEnum

class EngineStatus(StrEnum):
    IDLE    = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED  = "failed"