from src.app.domain.models.resource_identity import (
    StreamLocation, 
    LogicalURI, 
    PhysicalURI,
    PhysicalPath
)
from src.app.domain.services.resource_catalog import ResourceCatalog

class ResourceFactory:
    """
    The Classification Engine for URIs entering the system.
    SRP: Promotes raw strings into specialized ResourceIdentifiers 
    and determines the final StreamLocation (PhysicalPath or PhysicalURI).
    """
    
    def __init__(self, catalog: ResourceCatalog) -> None:
        """
        :param catalog: The Librarian responsible for resolving logical identities.
        """
        self._catalog = catalog

    def build(self, uri: str) -> StreamLocation:
        """
        The central decision engine for type-safe stream locations.
        
        Logic:
            1. Logical Branch: Promotes to LogicalURI -> Catalog resolve -> PhysicalPath.
            2. Physical Branch: Promotes to PhysicalURI (Direct Access).
            3. Firewall: Rejects unanchored/naked strings.
        """
        # 1. GOVERNED / INTERNAL (Identity-led)
        # We check for the 'registry://' protocol to trigger the Librarian.
        if uri.startswith("registry://"):
            # Value Object handles initial structural validation.
            logical = LogicalURI(uri) 
            
            # The Catalog returns a PhysicalPath (which satisfies StreamLocation).
            return self._catalog.resolve_uri(logical)
        
        # 2. DIRECT / EXTERNAL (Coordinate-led)
        # If it has a scheme but isn't registry, it's a raw coordinate (https, s3, file).
        if "://" in uri:
            # Returns a PhysicalURI (Direct-access coordinate).
            return PhysicalURI(uri)

        # 3. SECURITY FIREWALL (Naked path block)
        # Prevents '/etc/passwd' or './relative/path' from bypassing the registry.
        raise ValueError(
            f"Security Violation: '{uri}' is not a qualified ResourceIdentifier. "
            f"Use 'registry://[key]/path' for internal resources or a full URL for external ones."
        )