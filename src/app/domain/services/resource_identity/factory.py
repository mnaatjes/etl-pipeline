from typing import Dict, Type
from src.app.domain.models.resource_identity import (
    Coordinate,
    Address,
    Realm,
    ParsedURI,
    VirtualAddress,
    LocalAddress,
    NetworkAddress,
    MemoryAddress,
    SyntheticAddress,
    LocalCoordinate,
    NetworkCoordinate,
    MemoryCoordinate,
    SyntheticCoordinate,
    VirtualCoordinate,
    ResourceKey
)
from src.app.domain.services.resource_identity.catalog import ResourceCatalog
from src.app.registry.streams import StreamRegistry

class ResourceFactory:
    """
    The Classification Engine for URIs entering the system.
    SRP: Promotes raw strings into specialized Address/Coordinate objects.
    
    This factory is 'Registry-Driven': it uses the Catalog and StreamRegistry
    to determine the Realm of a protocol, avoiding hardcoded protocol lists.
    """
    
    # Internal Mapping: Domain Realm -> Domain Address Class
    REALM_ADDRESS_MAP: Dict[Realm, Type[Address]] = {
        Realm.LOCAL: LocalAddress,
        Realm.NETWORK: NetworkAddress,
        Realm.MEMORY: MemoryAddress,
        Realm.SYNTHETIC: SyntheticAddress,
        Realm.VIRTUAL: VirtualAddress,
    }

    def __init__(self, catalog: ResourceCatalog, registry: StreamRegistry) -> None:
        """
        :param catalog: The Librarian responsible for resolving logical identities.
        :param registry: Stream Adapter Registry
        """
        self._catalog = catalog
        self._registry = registry

    def build(self, uri: str) -> Coordinate:
        """
        The central decision engine for type-safe resource coordinates.
        """
        # 0. BASIC VALIDATION
        if "://" not in uri:
            raise ValueError(f"Security Violation: '{uri}' is not a qualified Resource Identifier!")

        # 1. PARSE
        parsed = ParsedURI.from_string(uri)
        protocol = parsed.protocol.lower()
        key = ResourceKey(parsed.authority)

        # 2. DISCOVER REALM (The Core Policy)
        realm = self._discover_realm(protocol, key)

        # 3. CLASSIFY (Realm -> Address)
        address_cls = self.REALM_ADDRESS_MAP.get(realm, Address)
        address = address_cls(uri)

        # 4. RESOLVE (Logical/Catalog-led)
        if protocol == "registry" or self._catalog.has_resource(protocol, key):
            return self._catalog.resolve(address)
        
        # 5. PROMOTE (Direct/Registry-led)
        if self._registry.is_supported(protocol):
            return self._promote_to_coordinate(address)
        
        # 6. SECURITY FIREWALL
        raise ValueError(
            f"Security Violation: '{uri}' is not a registered or governed ResourceIdentifier. "
            f"Register the protocol '{protocol}' or use the ResourceCatalog."
        )

    def _discover_realm(self, protocol: str, key: ResourceKey) -> Realm:
        """
        Registry-driven Realm discovery. No hardcoded protocols here.
        """
        # A. Hardcoded Internal Scheme
        if protocol == "registry":
            return Realm.VIRTUAL
            
        # B. Catalog Discovery (Internal Anchors)
        if self._catalog.has_resource(protocol, key):
            return self._catalog.get_realm(key)
            
        # C. Registry Discovery (External Adapters)
        if self._registry.is_supported(protocol):
            return self._registry.get_registration(protocol).realm
            
        # D. Default / Unknown
        return Realm.VIRTUAL

    def _promote_to_coordinate(self, address: Address) -> Coordinate:
        """
        Direct promotion for trusted, registered protocols.
        """
        if address.is_local:
            return LocalCoordinate(
                path=address.parsed.path, 
                protocol=address.protocol, 
                key=address.key
            )
            
        if address.is_remote:
            return NetworkCoordinate(url=address.raw_value, key=address.key)
            
        if address.is_memory:
            return MemoryCoordinate(reference=address.parsed.authority, key=address.key)
            
        if address.is_synthetic:
            return SyntheticCoordinate(generator_id=address.raw_value, key=address.key)
            
        return VirtualCoordinate(virtual_path=address.raw_value, key=address.key)
