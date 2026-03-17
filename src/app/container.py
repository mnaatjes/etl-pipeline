# src/app/container.py
# Libs and Frameworks
from typing import Any, Dict, Type, Union, TypeVar
# Runtime Imports
from src.app.domain.models.app_config import AppConfig
from src.app.use_cases.manager import StreamManager
from src.app.use_cases.pipeline_runner import PipelineRunner
from src.app.domain.services.context_orchestrator import ContextOrchestrator

# Define a Generic Type Var
T = TypeVar("T")

class ServiceContainer:

    def __init__(self) -> None:

        # Container
        self._services: Dict[Union[Type[Any], str], Any] = {}

    def bind(self, key:Union[Type[T], str], instance:Any) -> None:
        """Stores a Service Instance (dependency) in the container"""
        self._services[key] = instance

    def get(self, key:Union[Type[T], str]) -> T:
        """Retrieves a Service"""
        instance = self._services.get(key)
        # Validate
        if instance is None:
            # Error reporting based on Type-as-key implementation
            key_name = getattr(key, "__name__", str(key))
            raise KeyError(f"Service key '{key_name}' not found in Container!")
        # Return stored instance
        return instance

    @property
    def version(self) -> str:
        """Framework API Version"""
        return self.get("api_version")

    @property
    def settings(self) -> AppConfig:
        # TODO: Alter Access
        return self.get(AppConfig)
    
    @property
    def stream_manager(self) -> StreamManager:
        return self.get(StreamManager)
    
    @property
    def pipeline_runner(self) -> PipelineRunner:
        return self.get(PipelineRunner)
    
    @property
    def orchestrator(self) -> ContextOrchestrator:
        """Provides the Context Orchestrator (trace_id, overrides, settings) Service"""
        return self.get(ContextOrchestrator)