from typing import List, Optional, Any
from src.app.use_cases.manager import StreamManager
from src.app.registry.engines import EngineRegistry
from src.app.domain.models.pipeline.blueprint import PipelineBlueprint
from src.app.ports.output.middleware_processor import MiddlewareProcessor

class PipelineRunner:
    """
    The 'Conductor' of the Pipeline Subsystem.
    
    SRP: Orchestrates the high-level execution of a pipeline. It resolves 
    URI strings into real StreamHandles, constructs the PipelineBlueprint, 
    and manages the lifecycle of the chosen PipelineEngine.
    """

    def __init__(
        self, 
        manager: StreamManager, 
        engine_registry: EngineRegistry
    ) -> None:
        """
        Initializes the runner with its core collaborators.
        
        :param manager: Injected StreamManager for resource resolution.
        :param engine_registry: Injected Registry for execution strategies.
        """
        self._manager = manager
        self._engine_registry = engine_registry

    def execute_pipeline(
        self, 
        sources: List[str], 
        sinks: List[str], 
        processors: List[MiddlewareProcessor], 
        engine_type: str = "local", 
        trace_id: Optional[str] = None,
        **overrides
    ) -> None:
        """
        The Pipeline Execution Lifecycle.
        
        1. Resolves all URI strings into Smart StreamHandles.
        2. Constructs the immutable PipelineBlueprint (The Job Ticket).
        3. Selects and initializes the PipelineEngine.
        4. Triggers the engine's execution loop within a context manager.
        """
        # 1. FINAL INTEGRITY GUARD (One last check before resolution)
        if not sinks:
            raise ValueError(
                "Illegal Pipeline Operation: No destination defined. "
                "You must call .to(uri) before execution."
            )

        # 2. RESOLUTION: Promote URIs to Smart Handles via StreamManager
        # Ensure the pipeline's trace_id is injected into every handle.
        overrides["trace_id"] = trace_id

        source_handles = [
            self._manager.get_handle(uri, **overrides)
            for uri in sources
        ]
        
        sink_handles = [
            self._manager.get_handle(uri, as_sink=True, **overrides)
            for uri in sinks
        ]

        # 3. BLUEPRINT CREATION (The 'Bill of Materials')
        blueprint = PipelineBlueprint(
            sources=source_handles,
            sinks=sink_handles,
            processors=processors
        )

        # 4. ENGINE SELECTION & EXECUTION
        engine_cls = self._engine_registry.get_engine_cls(engine_type)
        
        # Engines are transient objects initialized per-run
        engine = engine_cls(trace_id=trace_id)

        # 5. LIFECYCLE HANDSHAKE (Setup -> Execute -> Shutdown)
        with engine.setup(blueprint) as executor:
            executor.execute()
