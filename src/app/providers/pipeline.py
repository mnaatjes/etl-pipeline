# src/app/providers/pipeline.py

from src.app.ports.input.module import AppModule
from src.app.container import ServiceContainer

# Registries & Use Cases
from src.app.registry.engines import EngineRegistry
from src.infrastructure.engines.local import LocalPipelineEngine
from src.app.use_cases.pipeline_runner import PipelineRunner
from src.app.use_cases.manager import StreamManager

class PipelineModule(AppModule):
    """
    Workflow Provider: Responsible for the "Engine" (PipelineRunner).
    """
    def register(self, container: ServiceContainer) -> None:
        """Phase 1: Foundation (Engine Registry)"""
        # 1. Instantiate and bind the EngineRegistry
        registry = EngineRegistry()
        
        # 2. Map Infrastructure (The Engine Inventory)
        registry.register("local", LocalPipelineEngine)
        
        container.bind(EngineRegistry, registry)

    def boot(self, container: ServiceContainer) -> None:
        """Phase 2: Orchestration (PipelineRunner)"""
        # 1. Instantiate and bind the PipelineRunner
        # Note: Depends on the StreamManager
        runner = PipelineRunner(
            manager=container.get(StreamManager),
            engine_registry=container.get(EngineRegistry)
        )
        container.bind(PipelineRunner, runner)

    def teardown(self, container: ServiceContainer) -> None:
        """Stop any active pipeline engines."""
        pass
