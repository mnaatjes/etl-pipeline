from typing import Any, Dict, Optional

# Domain Imports
from src.app.domain.models.resource_identity import StreamLocation, PhysicalPath, PhysicalURI
from src.app.domain.models.app_config import AppConfig

# Service/Port Imports
from src.app.domain.services.resource_factory import ResourceFactory
from src.app.domain.services.resource_catalog import ResourceCatalog
from src.app.domain.services.settings_resolver import SettingsResolver
from src.app.ports.output.datastream import DataStream
from src.app.registry.streams import StreamRegistry

class StreamManager:
    """
    The Orchestrator of the DataStream lifecycle.
    
    SRP: Handles the transition from a raw URI string to a fully-instantiated 
    Infrastructure Adapter. It uses the ResourceFactory to normalize identity 
    and the SettingsResolver to calculate the final configuration.
    """
    def __init__(
        self, 
        registry: StreamRegistry, 
        factory: ResourceFactory, 
        catalog: ResourceCatalog,
        app_config: AppConfig, 
        resolver: SettingsResolver
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
        self._app_config = app_config
        self._resolver = resolver

    def get_stream(
        self,
        uri: str,
        as_sink: bool = False,
        **overrides
    ) -> DataStream:
        """
        Main entry point to obtain a ready-to-use DataStream.
        """
        # 1. CLASSIFY & RESOLVE: Promote the raw string to a high-res Location
        # This handles either Catalog resolution (Internal) or Direct wrapping (External)
        location: StreamLocation = self._factory.build(uri)

        # 2. IDENTIFY: Determine the protocol required to find the blueprint
        # We ask the location object itself or the catalog for the protocol
        protocol = self._get_protocol_for_location(location)

        # 3. DISCOVER: Get the 'Blueprint' for this protocol
        blueprint = self._registry.get_registration(protocol)

        # 4. POLICY CHECK: If a blueprint has a secondary resolution/validation policy
        # This acts as a final 'Contextual Guard' before instantiation.
        if blueprint.policy:
            # We pass the high-res location object to the policy
            blueprint.policy.validate_access(location)
        
        # 5. CALCULATE: Run the Settings Waterfall (Global -> Local Overrides)
        settings = self._resolver.resolve(self._app_config, overrides)

        # 6. INSTANTIATE: Hire the Worker (Adapter) and hand it the Badge (Location)
        return blueprint.adapter_cls(
            uri=location,
            as_sink=as_sink,
            policy=blueprint.policy,
            **settings
        )

    # --- Private Helpers ---

    def _get_protocol_for_location(self, location: StreamLocation) -> str:
        """
        Extracts the protocol from the location object.
        - PhysicalPath: Asks the Catalog what protocol is mapped to the key.
        - PhysicalURI: Asks the URI what its scheme is (e.g., 'https').
        """
        if isinstance(location, PhysicalPath):
            # Internal resources need their protocol looked up by key
            return self._catalog.get_protocol(location.key)
        
        if isinstance(location, PhysicalURI):
            # External resources carry their protocol in the scheme
            return location.protocol
            
        raise TypeError(f"Unsupported StreamLocation type: {type(location)}")
    
    # --- Action Methods ---

    def read(self, uri: str) -> Any:
        """
        Convenience method to open a stream, read its entire contents, and close it.
        Perfect for small config files or JSON payloads.
        """
        with self.get_stream(uri, as_sink=False) as stream:
            # We must consume the generator while the stream is open
            return list(stream.read())

    def write(self, uri: str, data: Any) -> None:
        """
        Convenience method to open a stream for writing, commit data, and close it.
        """
        # Domain Import required for wrapping
        from src.app.domain.models.envelope import Envelope
        
        with self.get_stream(uri, as_sink=True) as stream:
            stream.write(Envelope(payload=data))

    def exists(self, uri: str) -> bool:
        """
        Checks if the resource exists without opening a full stream.
        Delegates the 'exists' check to the protocol-specific Adapter.
        """
        # We still need to classify the URI to find the right blueprint
        location = self._factory.build(uri)
        protocol = self._get_protocol_for_location(location)
        blueprint = self._registry.get_registration(protocol)

        # Adapters should implement a static or class method for 'exists' 
        # to avoid instantiating the whole stream object.
        return blueprint.adapter_cls.exists(location)

    # --- Discovery & Validation Methods ---

    def resolve(self, uri: str) -> StreamLocation:
        """
        Exposes the resolution logic. 
        Returns the PhysicalPath or PhysicalURI without opening a stream.
        Useful for debugging or pre-checking paths.
        """
        return self._factory.build(uri)

    def validate_resource(self, uri: str) -> bool:
        """
        Performs a 'Dry Run' of the entire resolution and policy check.
        Returns True if the URI is well-formed, registered, and passes 
        security boundaries.
        """
        try:
            location = self.resolve(uri)
            protocol = self._get_protocol_for_location(location)
            blueprint = self._registry.get_registration(protocol)
            
            if blueprint.policy:
                blueprint.policy.validate_access(location)
            return True
        except (ValueError, KeyError, PermissionError, TypeError):
            # In a High-Resolution architecture, we catch specific domain 
            # errors to indicate a 'False' validation state.
            return False

    # --- Configuration Methods ---

    def add_resource(self, key: str, protocol: str, anchor: Any) -> None:
        """
        Registers a new physical anchor in the Resource Catalog.
        
        :param key: The logical nickname (e.g., 'scans').
        :param protocol: The protocol required to access it (e.g., 'posix').
        :param anchor: The physical root (e.g., Path('/srv/data')).
        """
        # If the protocol is POSIX, we ensure the anchor is a Path object
        if protocol == "posix" and isinstance(anchor, str):
            from pathlib import Path
            anchor = Path(anchor)
            
        self._catalog.add_anchor(key=key, protocol=protocol, anchor=anchor)
