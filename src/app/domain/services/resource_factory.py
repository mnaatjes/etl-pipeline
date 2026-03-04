from src.app.domain.models.resource_identity import (
    StreamLocation, 
    LogicalURI, 
    PhysicalURI,
    PhysicalPath,
    ResourceKey
)
from src.app.domain.services.resource_catalog import ResourceCatalog
from src.app.registry.streams import StreamRegistry

class ResourceFactory:
    """
    The Classification Engine for URIs entering the system.
    SRP: Promotes raw strings into specialized ResourceIdentifiers 
    and determines the final StreamLocation (PhysicalPath or PhysicalURI).
    """
    
    def __init__(self, catalog: ResourceCatalog, registry:StreamRegistry) -> None:
        """
        :param catalog: The Librarian responsible for resolving logical identities.
        :param registry: Stream Adapter Registry
        """
        self._catalog = catalog
        self._registry = registry

    def build(self, uri: str) -> StreamLocation:
        """
        The central decision engine for type-safe stream locations.
        
        Logic:
            1. Logical Branch: Promotes to LogicalURI -> Catalog resolve -> PhysicalPath.
            2. Physical Branch: Promotes to PhysicalURI (Direct Access).
            3. Firewall: Rejects unanchored/naked strings.
        """
        # 1. GOVERNED / INTERNAL (Identity-led)
        # Ensure protocol is present
        if "://" not in uri:
            raise ValueError(f"Security Violation: '{uri}' is not a qualified Resource Identifier!")

        # Store incoming as candidate
        logical_candidate = LogicalURI(uri)
        scheme = logical_candidate.protocol
        key = logical_candidate.key

        # 1. IDENTITY CHECKS: Mandatory "://registry..." 
        if scheme == "registry":
            return self._catalog.resolve_uri(logical_candidate)
        
        # 2. DISCOVERY: Is the Catalog Aware of the protocol
        if self._catalog.has_resource(scheme, key):
            return self._catalog.resolve_uri(logical_candidate)

        # 3. COORDINATE: Registry Discovered
        if self._registry.is_supported(scheme):
            return PhysicalURI(uri)
        
        # 4. SECURITY FIREWALL (Naked path block)
        raise ValueError(
            f"Security Violation: '{uri}' is not a qualified ResourceIdentifier. "
            f"Use 'registry://[key]/path' for internal resources or use "
            f"'<protocol>://[key]/path' for registered resources"
        )