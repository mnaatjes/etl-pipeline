# src/app/domain/services/resource_factory.py

from src.app.domain.services.resource_catalog import ResourceCatalog

class LocationFactory:
    """
    The Classification Engine for URIs entering the system.
    SRP: Promotes raw strings into specialized ResourceIdentifiers 
    and determines the final StreamLocation.
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
            1. Logical Branch: Promotes to LogicalURI and resolves via Catalog 
               to produce a ValidatedPath.
            2. Physical Branch: Promotes to PhysicalURI (Direct Access).
            3. Firewall: Rejects anything that isn't a qualified ResourceIdentifier.
        """
        # 1. GOVERNED / INTERNAL (The Identity Branch)
        # If it's a registry URI, we must resolve it through our trusted Librarian.
        if uri.startswith("registry://"):
            # LogicalURI constructor handles structural validation
            logical = LogicalURI(uri) 
            # Catalog returns ValidatedPath (one branch of StreamLocation)
            return self._catalog.resolve_uri(logical)
        
        # 2. DIRECT / EXTERNAL (The Physical Branch)
        # If it has a scheme but isn't registry://, it's a direct coordinate.
        if "://" in uri:
            # PhysicalURI constructor handles validation (no registry, must have ://)
            # This directly satisfies the other branch of StreamLocation
            return PhysicalURI(uri)

        # 3. SECURITY FIREWALL
        # If we reach here, it's a naked path or garbage. 
        # On a Linux system, this prevents accidental root-access or relative-path leaks.
        raise ValueError(
            f"Unqualified ResourceIdentifier: '{uri}'. "
            f"Resources must be Logical (registry://) or Physical (e.g., https://)."
        )