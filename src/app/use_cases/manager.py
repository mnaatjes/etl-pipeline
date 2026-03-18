from typing import Any, Dict, Optional, Iterator
from uuid import uuid4

# Domain Imports
#from src.app.domain.models.resource_identity import StreamLocation, PhysicalPath, PhysicalURI, ResourceKey
from src.app.domain.models.app_config import AppConfig
from src.app.domain.models.streams import StreamHandle, StreamContext, StreamCapacity
from src.app.domain.models.packet import Packet
from src.app.domain.models.session_context import SessionContext
# Service/Port Imports
#from src.app.domain.services.resource_factory import ResourceFactory
#from src.app.domain.services.resource_catalog import ResourceCatalog
from src.app.registry.streams import StreamRegistry
#from src.app.domain.services.context_orchestrator import ContextOrchestrator
#from src.app.domain.services.traceability_provider import TraceabilityProvider
#from src.app.domain.services.settings_resolver import SettingsResolver

class StreamManager:
    """
    The Smart Gateway Orchestrator.
    
    SRP: Manages the resource lifecycle by resolving identities, 
    negotiating capabilities, and injecting traceability context.
    """
    def __init__(
        self, 
        registry: StreamRegistry, 
        factory: ResourceFactory, 
        catalog: ResourceCatalog,
        #app_config: AppConfig, 
        orchestrator: ContextOrchestrator
    ) -> None:
        """
        :param registry: Catalog of blueprints (Adapter Classes and Policies).
        :param factory: Classifier that promotes strings to StreamLocations.
        :param catalog: Librarian that provides protocol metadata for internal keys.
        :param app_config: Global settings (Tier 1).
        :param resolver: The Waterfall Engine for settings resolution.
        """
        self._registry = registry
        self._factory = factory
        self._catalog = catalog
        #self._app_config = app_config
        self._orchestrator = orchestrator

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
        # 1. CLASSIFY & RESOLVE: 
        # - String -> StreamLocation
        # - Determine the protocol
        # - Create blueprint
        location: StreamLocation = self._factory.build(uri)
        protocol  = self._get_protocol_for_location(location)
        blueprint = self._registry.get_registration(protocol)

        # 2. PROMOTION: Raw Context -> Domain StreamContext
        stream_context = StreamContext(
            origin=uri,
            current=str(location),
            trace_id=session_context.trace_id
        )

        # 3. RESOLVE: Settings
        settings = self._orchestrator.resolve_settings(context=session_context)

        # 4. POLICY CHECK: Contextual Guard
        if blueprint.policy:
            blueprint.policy.validate_access(location)

        # 5. INSTANTIATE: Context-Aware Adapter
        adapter = blueprint.adapter_cls(
            uri=location,
            context=stream_context,
            as_sink=as_sink,
            policy=blueprint.policy,
            **settings
        )

        # 6. NEGOTIATE: Wrap in a Smart Handle
        return StreamHandle(
            adapter=adapter,
            capacity=adapter.capacity,
            context=stream_context
        )

    # --- Private Helpers ---

    def _get_protocol_for_location(self, location: StreamLocation) -> str:
        """
        Extracts the protocol from the location object.
        """
        if isinstance(location, PhysicalPath):
            return self._catalog.get_protocol(location.key)
        
        if isinstance(location, PhysicalURI):
            return location.protocol
            
        raise TypeError(f"Unsupported StreamLocation type: {type(location)}")
    
    # --- Action Methods ---

    def read(self, uri: str, **overrides) -> Iterator[Packet]:
        """
        Convenience method to read traceable Packets from a URI.
        """
        handle = self.get_handle(uri, as_sink=False, **overrides)
        with handle as stream:
            yield from stream.read()

    def write(self, uri: str, data: Any, **overrides) -> None:
        """
        Convenience method to write data to a stream.
        """
        handle = self.get_handle(uri, as_sink=True, **overrides)
        with handle as stream:
            stream.write(data)

    def exists(self, uri: str) -> bool:
        """
        Checks if the resource exists without opening a full stream.
        """
        location = self._factory.build(uri)
        protocol = self._get_protocol_for_location(location)
        blueprint = self._registry.get_registration(protocol)

        return blueprint.adapter_cls.exists(location)

    # --- Discovery & Validation Methods ---

    def resolve(self, uri: str) -> StreamLocation:
        """Exposes the resolution logic."""
        return self._factory.build(uri)

    def validate_resource(self, uri: str) -> bool:
        """Performs a 'Dry Run' check."""
        try:
            location = self.resolve(uri)
            protocol = self._get_protocol_for_location(location)
            blueprint = self._registry.get_registration(protocol)
            
            if blueprint.policy:
                blueprint.policy.validate_access(location)
            return True
        except (ValueError, KeyError, PermissionError, TypeError):
            return False

    # --- Configuration Methods ---

    def add_resource(self, key: str, protocol: str, anchor: Any) -> None:
        """Registers a physical anchor in the Resource Catalog."""
        if protocol == "posix" and isinstance(anchor, str):
            from pathlib import Path
            anchor = Path(anchor)
            
        self._catalog.add_anchor(key=ResourceKey(key), protocol=protocol, anchor=anchor)
