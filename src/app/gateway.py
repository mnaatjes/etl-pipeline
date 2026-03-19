# src/app/gateway.py

from typing import Optional, Dict, Any, Iterator
from src.app.container import ServiceContainer
from src.app.domain.models.packet import Packet
from src.app.domain.models.streams import StreamHandle

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
            container: Optional[ServiceContainer] = None
    ) -> None:
        # 1. IoC CONTAINER
        if container:
            self._container = container
        else:
            from src.app.bootstrap import Bootstrap
            self._container = Bootstrap.initialize(overrides=config or {})

        # 2. SESSION CONTEXT
        # Build the initial context (Passport) for this gateway instance
        session_manager = self._container.session_manager
        self._context = session_manager.build_context(
            session_trace=trace_id, 
            **(config or {})
        )

        # 3. INTERNAL ORCHESTRATORS
        self._manager  = self._container.stream_manager
        self._pipeline = self._container.pipeline_runner

    # --- STREAM OPERATIONS ---

    def read(self, uri: str, **overrides) -> Iterator[Packet]:
        """Reads all packets from a URI using the gateway context."""
        # TODO: Implement context merging for overrides
        return self._manager.read(uri, session_context=self._context)

    def write(self, uri: str, data: Any, **overrides) -> None:
        """Writes data to a URI using the gateway context."""
        self._manager.write(uri, session_context=self._context, data=data)

    def get_handle(self, uri: str, as_sink: bool = False, **overrides) -> StreamHandle:
        """Requests a Smart Handle for advanced I/O."""
        return self._manager.get_handle(uri, session_context=self._context, as_sink=as_sink)

    # --- CONFIGURATION ---

    def add_resource(self, key: str, protocol: str, anchor: Any) -> None:
        """Registers a physical anchor in the resource catalog."""
        self._manager.add_resource(key=key, protocol=protocol, anchor=anchor)
