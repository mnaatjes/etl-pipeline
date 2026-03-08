# src/app/registry/engines.py

from typing import Dict, Type
from src.app.ports.output.pipeline_engine import PipelineEngine

class PipelineRegistry:
    """
    Library for pluggable Pipeline Engines
    """
    def __init__(self) -> None:
        self._engines: Dict[str, Type[PipelineEngine]] = {}


    def register(self, engine_name:str, engine_cls:Type[PipelineEngine]) -> None:
        """Assign to registry"""
        self._engines[engine_name] = engine_cls

    def get_engine(self, engine_name:str) -> Type[PipelineEngine]:
        """Retrieves the PipelineEngine which has been registered under 'engine_name' key"""
        if engine_name not in self._engines:
            available = ", ".join(self._engines.keys())
            raise ValueError(
                f"Unsupported Engine Name: '{engine_name}' "
                f"Please select from the following: {available}"
            )
        
        # Return
        return self._engines[engine_name]

    def has_engine(self, engine_name:str) -> bool:
        """Helper to see if engine name exists"""
        return engine_name in self._engines