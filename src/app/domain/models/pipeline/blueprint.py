# src/app/domain/models/pipeline/blueprint.py
from dataclasses import dataclass, field
from typing import Any, Optional, List

#  Domain Identity Imports
from src.app.domain.models.resource_identity import StreamLocation
from src.app.domain.models.streams.stream_handle import StreamHandle
from src.app.ports.output.middleware_processor import MiddlewareProcessor

@dataclass(frozen=True)
class PipelineBlueprint:
    """
    Bill of Materials for the Pipeline Execution

    Responsibilities:
    - Holds the resolved Source and Sink Handles
    - Maintains ordered list of Middleware Processors
    - Provides a single, immutable 'Job Ticket' for the Pipeline Engine
    """

    # Origin and Destination
    source: StreamHandle
    sink: StreamHandle

    # Processors / Middleware
    processors: List[MiddlewareProcessor] = field(default_factory=list)

    # Validation and Value Correction
    def __post_init__(self):
        """Validation: Ensure Blueprint is viable"""
        # Validate source and sink
        if not self.source.capacity.is_readable:
            raise ValueError(f"Pipeline Source {self.source.uri} is NOT Readable!")
        if not self.sink.capacity.is_writable:
            raise ValueError(f"Pipeline Sink {self.sink.uri} is NOT Writeable!")