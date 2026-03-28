# src/app/use_cases/manager.py
from typing import Any, Dict, Optional, Iterator, List
from src.app.domain.models.app_config import AppConfig
from src.app.domain.models.streams import StreamHandle, StreamContext, StreamCapacity
from src.app.domain.models.packet import Packet
from src.app.domain.models.session_context import SessionContext
from src.app.domain.models.resource_identity import Coordinate, Realm, ResourceKey
from src.app.domain.services.resource_identity import ResourceManager
from src.app.domain.services.session_context import SessionManager
from src.app.ports.output.middleware_processor import MiddlewareProcessor

class StreamManager:
    """
    The Smart Gateway Orchestrator.
    
    This use-case service manages the resource lifecycle by resolving 
    identities, negotiating capabilities, and injecting traceability 
    context into orchestrated StreamHandles.
    """
    
    def __init__(
        self, 
        resource_manager: ResourceManager,
        session_manager: SessionManager
    ) -> None:
        """
        Initializes the StreamManager with required subsystem facades.
        
        Args:
            resource_manager (ResourceManager): The identity subsystem authority.
            session_manager (SessionManager): The context and settings authority.
        """
        self._resources = resource_manager
        self._sessions  = session_manager

    def get_handle(
        self,
        uri: str,
        session_context: SessionContext,
        as_sink: bool = False,
        processors: Optional[List[MiddlewareProcessor]] = None
    ) -> StreamHandle:
        """
        Requests an orchestrated Smart Handle for a resource.
        
        This is the primary entry point for context-aware I/O. It coordinates 
        resolution, policy validation, settings resolution, and adapter 
        instantiation.
        
        Args:
            uri (str): The logical or physical resource address.
            session_context (SessionContext): The passport for this execution.
            as_sink (bool): Whether to open the stream for writing.
            processors (Optional[List[MiddlewareProcessor]]): Initial 
                transformations to attach to the handle.
                
        Returns:
            StreamHandle: The ready-to-use dashboard and orchestrator.
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

        # 6. NEGOTIATE: Wrap in an Orchestrated StreamHandle
        return StreamHandle(
            adapter=adapter,
            capacity=adapter.capacity,
            context=stream_context,
            processors=processors
        )

    # --- ACTION METHODS ---

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
        
        self._resources.validate_policy(src_coord)
        self._resources.validate_policy(dest_coord)
        
        if src_coord.protocol != dest_coord.protocol:
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
        """Performs a 'Dry Run' check via the identity subsystem."""
        return self._resources.is_supported_uri(uri)

    # --- CONFIGURATION METHODS ---

    def add_resource(self, key: str, protocol: str, anchor: Any) -> None:
        """
        Registers a physical anchor in the Resource Catalog.
        
        This method delegates to the identity subsystem authority.
        """
        self._resources.register_resource(key, protocol, anchor)

    # --- MIDDLEWARE METHODS ---

    def wrap(self, handle: StreamHandle, processors: List[MiddlewareProcessor]) -> StreamHandle:
        """
        Orchestration: Decorates an existing handle with new processors.
        """
        for p in processors:
            handle.add_processor(p)
        return handle
    
    def validate_processors(self) -> None:
        """Future: Ensures subject compatibility in a processor chain."""
        pass

    def get_available_processors(self) -> List[Dict[str, str]]:
        """Future: Lists globally available processor blueprints."""
        return []

    # --- DISCOVERY & UTILITY BRIDGES ---

    def resolve(self, uri: str) -> Coordinate:
        """Exposes the identity resolution logic."""
        return self._resources.resolve_resource(uri)
    
    def get_resources(self) -> Dict[str, Dict[str, str]]:
        """Discovery: Returns a snapshot of the resource catalog."""
        return self._resources.get_resource_map()
    
    def is_supported_uri(self, uri: str) -> bool:
        """Discovery: Checks if a URI is supported."""
        return self._resources.is_supported_uri(uri)
    
    def is_supported_protocol(self, protocol: str) -> bool:
        """Discovery: Checks if a protocol driver is loaded."""
        return self._resources.is_supported_protocol(protocol)
    
    def get_supported_protocols(self) -> List[str]:
        """Discovery: Returns all supported protocols."""
        return self._resources.get_supported_protocols()
    
    def has_resource(self, protocol: str, key: str) -> bool:
        """Discovery: Checks for a specific registration."""
        return self._resources.has_resource(protocol, key)

    def get_registered_adapter(self, protocol: str) -> str:
        """Discovery: Returns the adapter class name for a protocol."""
        return self._resources.get_registered_adapter(protocol)
