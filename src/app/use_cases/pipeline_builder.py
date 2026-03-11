from typing import List, Optional, Any
from src.app.domain.models.packet.payload import PayloadType, PayloadSubject
from src.app.ports.output.middleware_processor import MiddlewareProcessor
from src.app.use_cases.pipeline_runner import PipelineRunner

class PipelineBuilder:
    """
    The 'Architect' (Proxy) of the Pipeline Subsystem.
    
    SRP: Provides a Fluent DSL for building a pipeline. It collects the 
    user's intent (URIs and Processors) and performs 'Contract Adjudication' 
    to ensure the middleware chain is type-safe. Once built, it proxies 
    the execution to the PipelineRunner.
    """
    
    def __init__(
        self, 
        runner: PipelineRunner, 
        initial_source_uri: str,
        trace_id: str
    ) -> None:
        """
        Initializes the builder with its target runner and initial state.
        
        :param runner: The long-lived orchestrator in the AppContext.
        :param initial_source_uri: The starting coordinate of the data flow.
        :param trace_id: Unique identifier for the pipeline session.
        """
        self._runner = runner
        self._trace_id = trace_id
        
        # Intent Collection State
        self._source_uris: List[str] = [initial_source_uri]
        self._sink_uris: List[str] = []
        self._processors: List[MiddlewareProcessor] = []
        
        # Internal Adjudication State
        # In StreamFlow, all raw source streams yield BYTES (protocol default).
        self._current_output_type: PayloadType = PayloadSubject.BYTES

    # --- FLUENT CONFIGURATION METHODS ---

    def and_from(self, uri: str) -> 'PipelineBuilder':
        """Adds an additional source to the pipeline (Sequential Fan-in)."""
        self._source_uris.append(uri)
        return self

    def through(self, processor: MiddlewareProcessor) -> 'PipelineBuilder':
        """
        Appends a transformation step and validates the contract.
        
        This method acts as the 'Adjudicator'. It fails fast if the 
        processor's input does not match the current stream output.
        
        :raises TypeError: If the pipeline contract is violated.
        """
        # 1. CONTRACT ADJUDICATION (High-Resolution Safety)
        if processor.input_subject != self._current_output_type:
            raise TypeError(
                f"Pipeline Contract Violation! {processor.name} expects "
                f"'{processor.input_subject}', but the previous step "
                f"is yielding '{self._current_output_type}'."
            )

        # 2. Update State (Move the chain forward)
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
        The Handover.
        
        Proxies the collected intent to the PipelineRunner for resolution 
        and execution.
        """
        return self._runner.execute_pipeline(
            sources=self._source_uris,
            sinks=self._sink_uris,
            processors=self._processors,
            engine_type=engine_type,
            trace_id=self._trace_id,
            **overrides
        )
