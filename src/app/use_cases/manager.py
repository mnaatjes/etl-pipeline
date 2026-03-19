from typing import Any, Dict, Optional, Iterator
from uuid import uuid4

# Domain Imports
#from src.app.domain.models.resource_identity import StreamLocation, PhysicalPath, PhysicalURI, ResourceKey
from src.app.domain.models.app_config import AppConfig
from src.app.domain.models.streams import StreamHandle, StreamContext, StreamCapacity
from src.app.domain.models.packet import Packet
from src.app.domain.models.session_context import SessionContext
from src.app.domain.models.resource_identity import Coordinate
# Service/Port Imports
from src.app.domain.services.resource_identity import ResourceManager
from src.app.domain.services.session_context import SessionManager
from src.app.registry.streams import StreamRegistry

class StreamManager:
    """
    The Smart Gateway Orchestrator.
    
    SRP: Manages the resource lifecycle by resolving identities, 
    negotiating capabilities, and injecting traceability context.
    """
    def __init__(
        self, 
        resource_manager: ResourceManager,
        session_manager: SessionManager
    ) -> None:
        """
        :param resource_manager: The Facade for the Resource Identity Subsystem.
        :param session_manager: The Facade for the Session Context Subsystem.
        """
        self._resources = resource_manager
        self._sessions  = session_manager

    def get_handle(
        self,
        uri: str,
        session_context: SessionContext,
        as_sink: bool = False,
    ) -> StreamHandle:
        """
        Requests a Smart Handle for a resource.
        This is the primary entry point for context-aware I/O.
        """
        # 1. RESOLVE & VALIDATE (What)
        coordinate = self._resources.resolve_resource(uri)
        self._resources.validate_policy(coordinate)
        
        # 2. DISCOVER BLUEPRINT (How)
        registration = self._resources.get_registration(coordinate.protocol)

        # 3. PROMOTION: Raw Context -> Domain StreamContext
        stream_context = StreamContext(
            origin=uri,
            current=str(coordinate),
            trace_id=session_context.trace_id
        )

        # 4. RESOLVE: Settings (The "Waterfall")
        settings = self._sessions.resolve_settings(context=session_context)

        # 5. INSTANTIATE: Context-Aware Adapter
        adapter = registration.adapter_cls(
            uri=coordinate,
            context=stream_context,
            as_sink=as_sink,
            policy=registration.policy,
            **settings
        )

        # 6. NEGOTIATE: Wrap in a Smart Handle
        return StreamHandle(
            adapter=adapter,
            capacity=adapter.capacity,
            context=stream_context
        )

    # --- Private Helpers ---

    # (Removed _get_protocol_for_location as logic is now in ResourceManager)
    
    # --- Action Methods ---

    def read(self, uri: str, session_context: SessionContext) -> Iterator[Packet]:
        """
        Convenience method to read traceable Packets from a URI.
        """
        handle = self.get_handle(uri, session_context=session_context, as_sink=False)
        with handle as stream:
            yield from stream.read()

    def write(self, uri: str, session_context: SessionContext, data: Any) -> None:
        """
        Convenience method to write data to a stream.
        """
        handle = self.get_handle(uri, session_context=session_context, as_sink=True)
        with handle as stream:
            stream.write(data)

    def exists(self, uri: str) -> bool:
        """
        Checks if the resource exists without opening a full stream.
        """
        coordinate = self._resources.resolve_resource(uri)
        registration = self._resources.get_registration(coordinate.protocol)
        return registration.adapter_cls.exists(coordinate)

    # --- Discovery & Validation Methods ---

    def resolve(self, uri: str) -> Coordinate:
        """Exposes the resolution logic."""
        return self._resources.resolve_resource(uri)

    def validate_resource(self, uri: str) -> bool:
        """Performs a 'Dry Run' check."""
        try:
            coordinate = self.resolve(uri)
            self._resources.validate_policy(coordinate)
            return True
        except (ValueError, KeyError, PermissionError, TypeError):
            return False

    # --- Configuration Methods ---

    def add_resource(self, key: str, protocol: str, anchor: Any) -> None:
        """Registers a physical anchor in the Resource Catalog."""
        # This delegatest to internal components via ResourceManager if needed, 
        # but for now we'll access the catalog directly if exposed, 
        # or we might want to add a method to ResourceManager.
        # Given current architecture, let's keep it simple.
        # TODO: Move this to ResourceManager facade
        pass
