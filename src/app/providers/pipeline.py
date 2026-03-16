# src/app/providers/pipeline.py

from src.app.ports.input.module import AppModule
from src.app.container import ServiceContainer
from src.app.registry.engines import EngineRegistry
from src.app.use_cases.pipeline_runner import PipelineRunner

class PipelineModule(AppModule):

    def register(self, container: ServiceContainer) -> None:
        # Register Pipeline Runner Dependencies
        container.bind(
            key="engine_registry",
            instance=EngineRegistry()
        )

    def boot(self, container: ServiceContainer) -> None:
        # Init the pipeline runner and bind to container
        runner = PipelineRunner(
            manager=container.get("stream_manager"),
            engine_registry=container.get("engine_registry")
        )

        container.bind(
            key="pipeline_runner",
            instance=runner
        )