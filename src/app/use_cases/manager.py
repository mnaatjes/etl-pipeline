from typing import Any, Dict, Optional, Iterator, List
from uuid import uuid4

# Domain Imports
#from src.app.domain.models.resource_identity import StreamLocation, PhysicalPath, PhysicalURI, ResourceKey
from src.app.domain.models.app_config import AppConfig
from src.app.domain.models.streams import StreamHandle, StreamContext, StreamCapacity
from src.app.domain.models.packet import Packet
from src.app.domain.models.session_context import SessionContext
from src.app.domain.models.resource_identity import Coordinate, Realm, ResourceKey
# Service/Port Imports
from src.app.domain.services.resource_identity import ResourceManager
from src.app.domain.services.session_context import SessionManager
from src.app.registry.streams import StreamRegistry
from src.app.ports.output.middleware_processor import MiddlewareProcessor

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

    def list(self, uri: str, session_context: SessionContext) -> Iterator[Coordinate]:
        """
        Discovery: Lists resources available under a logical directory or authority.
        """
        coordinate = self._resources.resolve_resource(uri)
        registration = self._resources.get_registration(coordinate.protocol)
        yield from registration.adapter_cls.list(coordinate)

    def info(self, uri: str, session_context: SessionContext) -> Dict[str, Any]:
        """
        Metadata: Retrieves technical details about a resource without opening a stream.
        """
        coordinate = self._resources.resolve_resource(uri)
        registration = self._resources.get_registration(coordinate.protocol)
        return registration.adapter_cls.info(coordinate)

    def wrap(self, handle: StreamHandle, processors: List[MiddlewareProcessor]) -> StreamHandle:
        """
        Orchestration: Decorates a Smart Handle with middleware processors.
        """
        # Inject the processors into the handle's adapter (The Wrapper Pattern)
        # We assume the handle's context is preserved.
        handle.inject_processors(processors)
        return handle

    def delete(self, uri: str, session_context: SessionContext) -> bool:
        """
        CRUD: Removes a physical resource from the underlying medium.
        """
        coordinate = self._resources.resolve_resource(uri)
        self._resources.validate_policy(coordinate)
        registration = self._resources.get_registration(coordinate.protocol)
        return registration.adapter_cls.delete(coordinate)

    def move(self, src_uri: str, dest_uri: str, session_context: SessionContext) -> bool:
        """
        CRUD: Relocates a resource from one logical URI to another.
        """
        src_coord = self._resources.resolve_resource(src_uri)
        dest_coord = self._resources.resolve_resource(dest_uri)
        
        # Policy checks for both source and destination
        self._resources.validate_policy(src_coord)
        self._resources.validate_policy(dest_coord)
        
        # For now, we assume intra-adapter move
        if src_coord.protocol != dest_coord.protocol:
            # Fallback to copy-and-delete for cross-protocol moves (Simplified)
            if self.copy(src_uri, dest_uri, session_context):
                return self.delete(src_uri, session_context)
            return False
            
        registration = self._resources.get_registration(src_coord.protocol)
        return registration.adapter_cls.move(src_coord, dest_coord)

    def copy(self, src_uri: str, dest_uri: str, session_context: SessionContext) -> bool:
        """
        CRUD: Duplicates a resource to a new logical destination.
        """
        src_coord = self._resources.resolve_resource(src_uri)
        dest_coord = self._resources.resolve_resource(dest_uri)
        
        self._resources.validate_policy(src_coord)
        self._resources.validate_policy(dest_coord)
        
        # Cross-adapter copy (Read from source, Write to destination)
        if src_coord.protocol != dest_coord.protocol:
            try:
                with self.get_handle(src_uri, session_context) as source:
                    with self.get_handle(dest_uri, session_context, as_sink=True) as sink:
                        for packet in source.read():
                            sink.write(packet.payload)
                return True
            except Exception:
                return False
                
        registration = self._resources.get_registration(src_coord.protocol)
        return registration.adapter_cls.copy(src_coord, dest_coord)

    def exists(self, uri: str) -> bool:
        """
        Checks if the resource exists without opening a full stream.
        """
        coordinate = self._resources.resolve_resource(uri)
        registration = self._resources.get_registration(coordinate.protocol)
        return registration.adapter_cls.exists(coordinate)

    def validate_resource(self, uri: str) -> bool:
        """Performs a 'Dry Run' check."""
        try:
            coordinate = self.resolve(uri)
            self._resources.validate_policy(coordinate)
            return True
        except (ValueError, KeyError, PermissionError, TypeError):
            return False

    # --- CONFIGURATION METHODS ---

    def add_resource(self, key: str, protocol: str, anchor: Any) -> None:
        """
        Registers a physical anchor in the Resource Catalog.
        
        :param key: The nickname/alias (e.g., 'scans').
        :param protocol: The implementation protocol (e.g., 'posix', 'http').
        :param anchor: The physical root (Path, URL, or raw string).
        """
        # 1. Promote raw anchor to a Coordinate
        from src.app.domain.models.resource_identity import LocalCoordinate, NetworkCoordinate
        
        # 2. Get registration for the realm
        registration = self._resources.get_registration(protocol)
        
        if registration.realm == Realm.LOCAL:
            coordinate = LocalCoordinate(
                path=str(anchor), 
                protocol=protocol, 
                key=ResourceKey(key)
            )
        elif registration.realm == Realm.NETWORK:
            coordinate = NetworkCoordinate(url=str(anchor), key=ResourceKey(key))
        else:
            raise ValueError(f"Unsupported realm for manual registration: {registration.realm}")

        # 2. Delegate to the Resource Facade
        self._resources.add_anchor(key=key, anchor=coordinate)

    # --- UTILITY METHODS ---

    def resolve(self, uri: str) -> Coordinate:
        """Exposes the resolution logic."""
        return self._resources.resolve_resource(uri)
    
    def get_resources(self) -> Dict[str, Dict[str, str]]:
        """"""
        return self._resources.get_resource_map()
    
    def is_supported_uri(self, uri:str) -> bool:
        """"""
        return self._resources.is_supported_uri(uri)
    
    def is_supported_protocol(self, protocol: str) -> bool:
        """"""
        return self._resources.is_supported_protocol(protocol)
    
    def get_supported_protocols(self) -> List[str]:
        """"""
        return self._resources.get_supported_protocols()
    
    def has_resource(self, protocol:str, key:str) -> bool:
        """"""
        return self._resources.has_resource(protocol, key)

    def get_registered_adapter(self, protocol:str) -> str:
        """"""
        return self._resources.get_registered_adapter(protocol)
