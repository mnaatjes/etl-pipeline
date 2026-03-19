# src/app/domain/services/resource_identity/manager.py
from src.app.domain.models.resource_identity import Coordinate
from src.app.domain.services.resource_identity.factory import ResourceFactory
from src.app.domain.services.resource_identity.catalog import ResourceCatalog
from src.app.registry.streams import StreamRegistry, ProtocolRegistration

class ResourceManager:
    """
    The Facade for the Resource Identity Subsystem.
    
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
        self._factory = factory
        self._catalog = catalog
        self._registry = registry

    def resolve_resource(self, uri: str) -> Coordinate:
        """
        Highest-level entry point. 
        Promotes a raw string into a secured, physical Coordinate.
        """
        return self._factory.build(uri)

    def get_registration(self, protocol: str) -> ProtocolRegistration:
        """
        Retrieves the adapter and policy registered for a technical protocol.
        """
        return self._registry.get_registration(protocol)

    def validate_policy(self, coordinate: Coordinate) -> bool:
        """
        Performs the 'Contextual Guard' pre-flight check.
        Ensures the coordinate doesn't violate registered security policies.
        """
        registration = self.get_registration(coordinate.protocol)
        
        if registration.policy:
            # Policy validation
            if not registration.policy.validate_access(coordinate):
                raise PermissionError(f"Policy Violation: Access denied for {coordinate}")
        
        return True

    def get_protocol(self, coordinate: Coordinate) -> str:
        """
        Determines the implementation protocol for a coordinate.
        """
        return coordinate.protocol

    # --- Configuration Methods ---

    def add_anchor(self, key: str, anchor: Coordinate) -> None:
        """
        Registers a physical root (anchor) in the Resource Catalog.
        
        :param key: The nickname/alias (e.g., 'scans').
        :param anchor: The physical root Coordinate.
        """
        from src.app.domain.models.resource_identity import ResourceKey
        self._catalog.add_anchor(key=ResourceKey(key), anchor=anchor)

    def register_boundary(self, protocol: str, boundary: any) -> None:
        """
        Registers a security boundary for a specific protocol.
        """
        self._catalog.register(protocol=protocol, boundary=boundary)

    # --- Discovery Helpers ---

    def is_supported(self, uri: str) -> bool:
        """
        Determines if the system is capable of handling the given URI.
        """
        try:
            coordinate = self.resolve_resource(uri)
            return self._registry.is_supported(coordinate.protocol)
        except (ValueError, KeyError):
            return False
