from typing import List, Optional, Any
from src.app.domain.models.pipeline.blueprint import PipelineBlueprint
from src.app.domain.models.packet.payload import PayloadType
from src.app.ports.output.middleware_processor import MiddlewareProcessor
from src.app.use_cases.manager import StreamManager
from src.app.registry.engines import EngineRegistry
from src.app.domain.services.traceability_provider import TraceabilityProvider

class PipelineBuilder:
    """
    The 'Architect' of the Pipeline Subsystem.
    
    SRP: Provides a Fluent DSL for configuring, validating, and building 
    a PipelineBlueprint. It acts as the 'Adjudicator' for type-safe 
    middleware chains.
    """
    
    def __init__(
        self, 
        manager: StreamManager, 
        engine_registry: EngineRegistry, 
        initial_source_uri: str,
        trace_id: Optional[str] = None
    ) -> None:
        """
        Initializes the builder with its core dependencies.
        
        :param manager: Injected StreamManager for resource resolution.
        :param engine_registry: Injected Registry for execution strategies.
        :param initial_source_uri: The starting coordinate of the data flow.
        :param trace_id: Optional ID injected from the StreamClient session.
        """
        self._manager = manager
        self._engine_registry = engine_registry
        
        # Configuration State
        self._source_uris: List[str] = [initial_source_uri]
        self._sink_uris: List[str] = []
        self._processors: List[MiddlewareProcessor] = []
        
        # Metadata & Traceability
        # Use the provider to resolve the ID (Priority B: Context/Orchestrator ID)
        self._trace_id: str = TraceabilityProvider.resolve(context_id=trace_id)
        
        # Internal Adjudication State
        # We assume initial source output is BYTES (default protocol behavior)
        self._current_output_type: PayloadType = PayloadType.BYTES

    # --- FLUENT CONFIGURATION METHODS ---

    def and_from(self, uri: str) -> 'PipelineBuilder':
        """Adds an additional source to the pipeline (Sequential Fan-in)."""
        self._source_uris.append(uri)
        return self

    def through(self, processor: MiddlewareProcessor) -> 'PipelineBuilder':
        """
        Appends a transformation step and validates the contract.
        
        Raises:
            TypeError: If the processor's input does not match the current output.
        """
        # 1. CONTRACT ADJUDICATION (High-Resolution Safety)
        if processor.input_subject != self._current_output_type:
            raise TypeError(
                f"Pipeline Contract Violation! {processor.name} expects "
                f"'{processor.input_subject.name}', but the previous step "
                f"is yielding '{self._current_output_type.name}'."
            )

        # 2. Update State
        self._processors.append(processor)
        self._current_output_type = processor.output_subject
        return self

    def to(self, uri: str) -> 'PipelineBuilder':
        """Adds a destination to the pipeline (Broadcast Fan-out)."""
        self._sink_uris.append(uri)
        return self

    # --- TERMINAL EXECUTION METHOD ---

    def run(self, engine_type: str = "local", **overrides) -> None:
        """
        The Conductor's Handover.
        Resolves handles, constructs the Blueprint, and triggers execution.
        """
        # 1. FINAL INTEGRITY GUARD
        if not self._sink_uris:
            raise ValueError(
                "Illegal Pipeline Operation: No destination defined. "
                "You must call .to(uri) before calling .run()."
            )

        # 2. RESOLUTION: Promote URIs to Smart Handles via StreamManager
        # Ensure the pipeline's trace_id is injected into every handle.
        overrides["trace_id"] = self._trace_id

        source_handles = [
            self._manager.get_handle(uri, **overrides)
            for uri in self._source_uris
        ]
        
        sink_handles = [
            self._manager.get_handle(uri, as_sink=True, **overrides)
            for uri in self._sink_uris
        ]

        # 3. BLUEPRINT CREATION (The 'Job Ticket')
        blueprint = PipelineBlueprint(
            sources=source_handles,
            sinks=sink_handles,
            processors=self._processors
        )

        # 4. ENGINE SELECTION & EXECUTION
        engine_cls = self._engine_registry.get_engine_cls(engine_type)
        engine = engine_cls(trace_id=self._trace_id)

        # 5. LIFECYCLE HANDSHAKE
        with engine.setup(blueprint) as executor:
            executor.execute()
