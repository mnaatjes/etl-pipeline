# src/app/providers/pipeline.py

from src.app.ports.input.module import AppModule
from src.app.container import ServiceContainer
from src.app.registry.engines import EngineRegistry
from src.app.use_cases.pipeline_runner import PipelineRunner
from src.app.use_cases.manager import StreamManager

class PipelineModule(AppModule):

    def register(self, container: ServiceContainer) -> None:
        # Register Pipeline Runner Dependencies
        container.bind(
            key=EngineRegistry,
            instance=EngineRegistry()
        )

    def boot(self, container: ServiceContainer) -> None:
        # Init the pipeline runner and bind to container
        runner = PipelineRunner(
            manager=container.get(StreamManager),
            engine_registry=container.get(EngineRegistry)
        )

        container.bind(
            key=PipelineRunner,
            instance=runner
        )