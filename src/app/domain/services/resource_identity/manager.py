# src/app/domain/services/resource_identity/manager.py
from src.app.domain.models.resource_identity import Coordinate
from src.app.domain.services.resource_identity.factory import ResourceFactory
from src.app.domain.services.resource_identity.catalog import ResourceCatalog
from src.app.registry.streams import StreamRegistry, AdapterBlueprint
from src.app.ports.input.resource_boundaries import ResourceBoundary
from typing import Dict, List

class ResourceManager:
    """
    The Facade for the Resource Identity Subsystem.
    
    This service is the 'Brain' of the identity layer, responsible for 
    translating logical intents into physical realities, enforcing 
    security policies, and managing the resource catalog.
    
    Responsibilities:
    - Promotion: String URI --> Coordinate (via ResourceFactory)
    - Blueprint Mapping: Finding the correct adapter blueprint (via StreamRegistry)
    - Policy Enforcement: Running pre-flight security checks (via StreamPolicy)
    - Protocol Discovery: Extracting technical protocols from coordinates
    """
    
    def __init__(
        self, 
        factory: ResourceFactory, 
        catalog: ResourceCatalog, 
        registry: StreamRegistry
    ) -> None:
        """
        Initializes the ResourceManager with its required internal services.
        
        Args:
            factory (ResourceFactory): The engine for URI classification.
            catalog (ResourceCatalog): The registry for anchors and boundaries.
            registry (StreamRegistry): The database of supported protocols.
        """
        self._factory = factory
        self._catalog = catalog
        self._registry = registry

    def resolve_resource(self, uri: str) -> Coordinate:
        """
        Highest-level entry point for identity resolution.
        
        Promotes a raw string (Logical URI or Physical Path) into a 
        secured, physical Coordinate object ready for I/O.
        
        Args:
            uri (str): The string to resolve (e.g., 'registry://scans/01.csv').
            
        Returns:
            Coordinate: The physical address, validated and secured.
            
        Example:
            >>> manager.resolve_resource("registry://scans/data.json")
            <LocalCoordinate: file:///srv/pipeline/scans/data.json>
        """
        return self._factory.build(uri)

    def get_registration(self, protocol: str) -> AdapterBlueprint:
        """
        Retrieves the technical blueprint for a specific protocol.
        
        Args:
            protocol (str): The technical protocol key (e.g., 'posix', 'http').
            
        Returns:
            AdapterBlueprint: The object containing the adapter class and policy.
            
        Raises:
            ValueError: If the protocol is not registered in the system.
        """
        return self._registry.get_registration(protocol)

    def validate_policy(self, coordinate: Coordinate) -> bool:
        """
        Performs the 'Contextual Guard' pre-flight check.
        
        Ensures the coordinate doesn't violate registered security policies 
        before a stream is opened.
        
        Args:
            coordinate (Coordinate): The physical address to validate.
            
        Returns:
            bool: True if the access is valid.
            
        Raises:
            PermissionError: If the policy validation fails.
        """
        registration = self.get_registration(coordinate.protocol)
        
        if registration.policy:
            if not registration.policy.validate_access(coordinate):
                raise PermissionError(f"Policy Violation: Access denied for {coordinate}")
        
        return True

    # --- CONFIGURATION METHODS ---

    def register_blueprint(self, blueprint: AdapterBlueprint) -> None:
        """
        Registers a complete adapter driver blueprint.
        
        This method coordinates between the Registry (for I/O) and the 
        Catalog (for Security) to ensure the protocol is fully supported.
        
        Args:
            blueprint (AdapterBlueprint): The complete driver definition.
            
        Example:
            >>> manager.register_blueprint(PosixFileBlueprint)
        """
        # 1. Register for IO
        self._registry.register(blueprint)

        # 2. Register for Security
        if blueprint.boundary:
            self._catalog.register(
                protocol=blueprint.protocol,
                boundary=blueprint.boundary
            )

    def register_boundary(self, protocol: str, boundary: ResourceBoundary) -> None:
        """
        Registers a standalone security boundary for a specific protocol.
        
        Args:
            protocol (str): The protocol the boundary protects.
            boundary (ResourceBoundary): The guard instance.
        """
        self._catalog.register(protocol=protocol, boundary=boundary)

    def register_resource(self, key: str, protocol: str, anchor: str) -> None:
        """
        Configuration: Promotes a raw anchor into a secured, registered Resource.
        
        This is the high-level entry point for adding logical nicknames 
        (anchors) to the framework. It automatically determines the correct 
        Coordinate type based on the protocol's Realm.
        
        Args:
            key (str): The logical nickname/alias (e.g., 'scans').
            protocol (str): The technical protocol (e.g., 'posix', 'http').
            anchor (str): The physical root (Path, URL, or raw string).
            
        Raises:
            ValueError: If the protocol is not supported or the Realm 
                does not support manual registration.
                
        Example:
            >>> manager.register_resource("scans", "posix", "/srv/data/scans")
        """
        # Import
        from src.app.domain.models.resource_identity import (
            LocalCoordinate,
            NetworkCoordinate,
            ResourceKey,
            Coordinate,
            Realm
        )

        # VALIDATE Protocol Support
        if not self.is_supported_protocol(protocol):
            raise ValueError(
                f"Configuration Error: Protocol '{protocol}' is NOT supported! "
                f"Available: {self.get_supported_protocols()}"
            )
        
        # DISCOVER Registration Details
        registration = self.get_registration(protocol)

        # CONSTRUCT the appropriate Coordinate based on Realm
        def promote_coordinate(realm: Realm, key: str, protocol: str, anchor: str) -> Coordinate:
            match realm:
                case Realm.LOCAL:
                    return LocalCoordinate(
                        path=str(anchor),
                        protocol=protocol,
                        key=ResourceKey(key)
                    )
                case Realm.NETWORK:
                    return NetworkCoordinate(
                        url=anchor,
                        protocol=protocol,
                        key=ResourceKey(key)
                    )
                case _:
                    raise ValueError(f"Manual Registration NOT Supported for Realm: {realm}")
        
        coordinate = promote_coordinate(registration.realm, key, protocol, anchor)

        self._catalog.add_anchor(key=ResourceKey(key), anchor=coordinate)

    # --- UTILITY METHODS ---

    def is_supported_uri(self, uri: str) -> bool:
        """
        Discovery: Determines if the system can handle the given URI.
        
        This performs a dry-run resolution to check for available drivers.
        
        Args:
            uri (str): The URI to test.
            
        Returns:
            bool: True if both identity and I/O driver are supported.
        """
        try:
            coordinate = self.resolve_resource(uri)
            return self._registry.is_supported(coordinate.protocol)
        except (ValueError, KeyError):
            return False
    
    def is_supported_protocol(self, protocol: str) -> bool:
        """
        Discovery: Checks if a technical driver is loaded for a protocol.
        
        Args:
            protocol (str): The protocol name (e.g., 'posix').
            
        Returns:
            bool: True if an adapter is registered.
        """
        return self._registry.is_supported(protocol)
    
    def get_resource_map(self) -> Dict[str, Dict[str, str]]:
        """
        Discovery: Returns a complete snapshot of all registered resources.
        
        Returns:
            Dict[str, Dict[str, str]]: A map of keys to their anchor and boundary info.
        """
        return self._catalog.get_snapshot()
    
    def has_resource(self, protocol: str, key: str) -> bool:
        """
        Discovery: Checks if a specific key is registered under a protocol.
        
        Args:
            protocol (str): The protocol to check within.
            key (str): The logical nickname to look for.
            
        Returns:
            bool: True if the resource exists in the catalog.
        """
        return self._catalog.has_resource(protocol, key)
    
    def get_registered_adapter(self, protocol: str) -> str:
        """
        Introspection: Retrieves the name of the adapter class for a protocol.
        
        Args:
            protocol (str): The technical protocol to inspect.
            
        Returns:
            str: The implementation class name (e.g., 'PosixFileStream').
        """
        registration = self.get_registration(protocol)
        return registration.adapter_cls.__name__
    
    def get_supported_protocols(self) -> List[str]:
        """
        Discovery: Lists all supported technical protocols.
        
        Returns:
            List[str]: A list of protocol strings (e.g., ['posix', 'http']).
        """
        registrations = self._registry.get_all()
        return list(registrations.keys())
