# src/app/gateway.py

from typing import Optional, Dict, Any, Iterator, List
from src.app.container import ServiceContainer
from src.app.domain.models.packet import Packet
from src.app.domain.models.streams import StreamHandle
from src.app.domain.models.resource_identity import Coordinate
from src.app.use_cases.pipeline_builder import PipelineBuilder
from src.app.ports.output.middleware_processor import MiddlewareProcessor

class Gateway:
    """
    The Slalom Smart Gateway.
    
    The primary entry point for the Slalom framework. It abstracts the 
    underlying orchestration of identity, session context, and stream management.
    """

    def __init__(
            self,
            config: Optional[Dict[str, Any]] = None,
            trace_id: Optional[str] = None,
            container: Optional[ServiceContainer] = None,
            **overrides
    ) -> None:
        # 0. MERGE Final Configuration
        final_config = {**(config or {}), **overrides}

        # 1. IoC CONTAINER
        if container:
            self._container = container
        else:
            from src.app.bootstrap import Bootstrap
            self._container = Bootstrap.initialize(overrides=final_config or {})

        # 2. SESSION CONTEXT
        # Pull SessionManager from ServiceContainer
        # Build the initial context (Passport) for this gateway instance
        
        session_manager = self._container.session_manager
        self._context   = session_manager.build_context(
            session_trace=trace_id, 
            **final_config
        )

        # 3. INTERNAL ORCHESTRATORS
        self._manager  = self._container.stream_manager
        self._pipeline = self._container.pipeline_runner

    # --- STREAM OPERATIONS ---

    def get_handle(self, uri: str, as_sink: bool = False, **overrides) -> StreamHandle:
        """Requests a Smart Handle for advanced I/O."""
        # Refine call_context
        call_context = self._context.spawn(**overrides)
        # Return Handle with refined SessionContext
        return self._manager.get_handle(uri, session_context=call_context, as_sink=as_sink)
    
    def read(self, uri: str, **overrides) -> Iterator[Packet]:
        """Reads all packets from a URI using the gateway context."""
        # Refine call_context
        call_context = self._context.spawn(**overrides)
        return self._manager.read(uri, session_context=call_context)

    def write(self, uri: str, data: Any, **overrides) -> None:
        """Writes data to a URI using the gateway context."""
        # Refine call_context
        call_context = self._context.spawn(**overrides)
        self._manager.write(uri, session_context=call_context, data=data)

    def list(self, uri: str, **overrides) -> Iterator[Coordinate]:
        """
        Discovery: Lists resources available under a logical directory or authority.
        
        :param uri: The logical URI or nickname (e.g., 'registry://scans/').
        :param overrides: Run-time settings to merge into the session context.
        :return: An iterator of Coordinate objects.
        """
        pass

    def info(self, uri: str, **overrides) -> Dict[str, Any]:
        """
        Metadata: Retrieves technical details about a resource without opening a stream.
        
        :param uri: The logical URI of the resource.
        :param overrides: Run-time settings to merge into the session context.
        :return: A dictionary containing resource metadata.
        """
        pass

    def exists(self, uri: str) -> bool:
        """
        Validation: Checks if a resource exists without opening a stream.
        
        :param uri: The logical URI to verify.
        :return: True if the resource exists, False otherwise.
        """
        pass

    def delete(self, uri: str, **overrides) -> bool:
        """
        CRUD: Removes a physical resource from its underlying medium.
        
        :param uri: The logical URI of the resource to delete.
        :param overrides: Run-time settings to merge into the session context.
        :return: True if successful.
        """
        pass

    def move(self, src_uri: str, dest_uri: str, **overrides) -> bool:
        """
        CRUD: Relocates a resource from one logical URI to another.
        
        :param src_uri: The current logical URI.
        :param dest_uri: The target logical URI.
        :param overrides: Run-time settings to merge into the session context.
        :return: True if relocation was successful.
        """
        pass

    def copy(self, src_uri: str, dest_uri: str, **overrides) -> bool:
        """
        CRUD: Duplicates a resource to a new logical destination.
        
        :param src_uri: The source logical URI.
        :param dest_uri: The target destination logical URI.
        :param overrides: Run-time settings to merge into the session context.
        :return: True if duplication was successful.
        """
        pass

    # --- ORCHESTRATION ---

    def pipeline(self, uri: str, **overrides) -> PipelineBuilder:
        """
        Fluent Entry Point: Initiates a new PipelineBuilder session.
        
        This is the 'Golden Path' for multi-step stream processing.
        
        :param uri: The starting source URI for the pipeline.
        :param overrides: Initial settings for the pipeline session.
        :return: A PipelineBuilder instance.
        """
        pass

    def wrap(self, handle: StreamHandle, processors: List[MiddlewareProcessor]) -> StreamHandle:
        """
        Decorates a Smart Handle with standalone middleware processors.
        
        :param handle: The existing StreamHandle to wrap.
        :param processors: List of middleware to apply.
        :return: A new StreamHandle with the transformation chain injected.
        """
        pass

    # --- CONFIGURATION ---

    def add_resource(self, key: str, protocol: str, anchor: Any) -> None:
        """Registers a physical anchor in the resource catalog."""
        self._manager.add_resource(key=key, protocol=protocol, anchor=anchor)
