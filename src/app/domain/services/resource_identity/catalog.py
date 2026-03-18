from typing import Dict

# Updated Imports: Sourced from the new identity package
from src.app.domain.models.resource_identity import (
    ResourceKey,
    Address,
    Coordinate,
    LocalCoordinate,
    Realm
)
from src.app.ports.input.resource_boundaries import ResourceBoundary

class ResourceCatalog:
    """
    The Domain Service responsible for resource discovery and security.
    Acts as the Librarian for the 'registry://' internal protocol.
    """
    def __init__(self):
        # PROMOTION
        # - Anchors are now Coordinates
        # - e.g. LocalCoordinate('tests/data/path/to/file')
        self._anchors: Dict[ResourceKey, Coordinate] = {}
        
        # PROMOTION
        # - Boundaries expect Coordinate as their scope root
        self._boundaries: Dict[str, ResourceBoundary] = {}

    def register(self, protocol: str, boundary: ResourceBoundary) -> None:
        """Registers a security guard to a specific protocol."""
        # PREVENT silent overwrites
        if protocol in self._boundaries:
            # STRICT: Notify protocol already registered
            raise ValueError(f"Protocol '{protocol}' is already registered!")
        
        # REGISTER Resource Boundary
        self._boundaries[protocol] = boundary

    def add_anchor(self, key: ResourceKey, anchor: Coordinate) -> None:
        """Associates a nickname (key) with a protocol and a physical root."""
        # DERIVE the protocol from the coordinate
        protocol = anchor.protocol

        # ENFORCE protocol check
        if protocol not in self._boundaries:
            raise ValueError(
                f"Configuration Error: Cannot add anchor for '{key}' "
                f"No Boundary registered for protocol: {protocol}"
            )

        # STORE as objects
        self._anchors[key] = anchor

    def resolve(self, address: Address) -> Coordinate:
        """
        Translates an Address (intent) into a secured Coordinate (physical reality)
        """
        # IDENTIFY: Get key (e.g. "scans")
        key = ResourceKey(address.key)

        # LOOKUP: Find protocol and anchor
        # - e.g. "posix" and "/path/to/file"
        protocol = self._get_protocol(key)
        anchor   = self._get_anchor(key)

        # DELIGATE: Boundary Port performs security check
        boundary = self._boundaries[protocol]

        # Return Coordinate produces by Boundary
        return boundary.resolve(address, anchor)


    # --- HELPER & METADATA METHODS ---

    def has_resource(self, protocol:str, key:ResourceKey|str) -> bool:
        """External Helper: Checks if protocol or key is registered"""
        if isinstance(key, str):
            key = ResourceKey(key)
        return key in self._anchors

    def _get_anchor(self, key: ResourceKey) -> Coordinate:
        """Internal Helper: Retrieves authorized Coordinate root"""
        if key not in self._anchors:
            raise KeyError(f"Metadata Error: Anchor for ResourceKey '{key}' NOT Found!")
        return self._anchors[key]

    def _get_protocol(self, key: ResourceKey) -> str:
        """Internal Helper: Derives protocol from the registered anchor"""
        return self._get_anchor(key).protocol

    def get_realm(self, key: ResourceKey) -> Realm:
        """Exposes the realm of a registered anchor."""
        return self._get_anchor(key).realm