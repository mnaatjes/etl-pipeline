# src/app/ports/output/pipeline_engine.py
from abc import ABC, abstractmethod
from typing import Any, Optional

from src.app.domain.models.pipeline.blueprint import PipelineBlueprint
from src.app.domain.models.pipeline.engine_status import EngineStatus
from src.app.domain.exceptions.pipeline.pipeline_execution_error import PipelineExecutionError

class PipelineEngine(ABC):
    """
    Abstract Pipeline Execution Engine (a strategy)
    Responsibilities:
    - Encapsulates 'How' data moves (Sequential, Concurrent, Distributed)
    - Manages Execution Lifecycle (Setup --> Execute --> Shutdown)
    - Enforces Resource Integrity
    """
    def __init__(self, trace_id:str) -> None:
        self.trace_id   = trace_id
        self.status     = EngineStatus.IDLE
        self._blueprint: Optional[PipelineBlueprint] = None

    @abstractmethod
    def setup(self, blueprint:PipelineBlueprint) -> 'PipelineEngine':
        """Prepare the engine with valid Blueprints"""
        self._blueprint = blueprint
        return self

    @abstractmethod
    def execute(self) -> None:
        """
        Core Execution Method Requirements:
        - Must catch implementation-specific errors (e.g. Connection Error, FileNotFoundError)
        - Re-raise as PipelineExecutionError
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """
        Resource Lifecycle Cleanup
        - Guarentees all handles in PipelineBlueprint are closed
        """
        self.status = EngineStatus.IDLE
    

    # --- INFRASTRUCTURE: Context Manager Support ---

    def __enter__(self) -> 'PipelineEngine':
        """Transition to RUNNING State and return the Engine for execute()"""
        if not self._blueprint:
            raise RuntimeError("Engine cannot start: setup(blueprint) was never called!!!")
        
        # Set status and return
        self.status = EngineStatus.RUNNING
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Finalize Engine State and Trigger Mandatory Shutdown"""
        if exc_type:
            self.status = EngineStatus.FAILED
        else:
            self.status = EngineStatus.SUCCESS

        # Ensure resources are freed
        self.shutdown()