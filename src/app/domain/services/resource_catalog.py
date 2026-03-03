# src/app/domain/services/resource_catalog.py
from typing import Dict, Any, TypeVar
from src.app.domain.models.types import ResourceKey, ValidatedPath, StreamLocation
from src.app.domain.models.logical_uri import LogicalURI
from src.app.ports.input.resource_boundary import ResourceBoundary

T = TypeVar("T")

class ResourceCatalog:
    """
    The Domain Service responsible for resource discovery and security.
    - Maintains the mapping of Logical Keys to Physical Anchors.
    - Specifically designated to be the gatekeeper for 'registry://' URIs
    - Logical Resources: registry://scans/data.json
    - Physical Transports: https://eddb.com/api or file://scans/data.json
    """
    def __init__(self):
        """
        Maps a ResourceKey (e.g. "downloads") to a physical Anchor (e.g. Path())
        - Anchors: Physical Root which defined the boundary; e.g. "/srv/data/"
        - ResourceKey: Alias / Nickname used to look-up anchors
        """
        self._anchors: Dict[ResourceKey, Any] = {}
        
        """
        Maps a Protocol (e.g. posix) to its specific ResourceBoundary implementation
        """
        self._boundaries: Dict[str, ResourceBoundary[Any]] = {}
        # Maps a ResourceKey to its Protocol Type
        self._key_protocols: Dict[ResourceKey, str] = {}

    def register(self, protocol: str, boundary: ResourceBoundary[Any]) -> None:
        """Registers a security guard to a specific protocol"""
        self._boundaries[protocol] = boundary

    def add_anchor(self, key: ResourceKey, protocol: str, anchor: Any) -> None:
        """Adds nickname (key) to catalog with its associated protocol and physical root"""
        if protocol not in self._boundaries:
            raise ValueError(f"No Boundary registered for protocol: {protocol}")
        
        self._anchors[key] = anchor
        self._key_protocols[key] = protocol

    # --- Core Logic Methods ---

    def resolve_uri(self, uri: LogicalURI) -> StreamLocation:
        """
        Universal resolver/translator from 'registry://path/file.xml' 
        to a technical StreamLocation.
        """
        # 1. Access the Key directly from the Value Object
        # We cast the smart property to a ResourceKey to match our dict keys.
        key = ResourceKey(uri.key)

        # 2. Verified Metadata Look-ups
        protocol = self._get_protocol(key)
        anchor   = self._get_anchor(key)
        
        # 3. Delegate to Boundary
        boundary = self._boundaries[protocol]

        # 4. Resolve via the specific security guard
        return boundary.resolve(uri, anchor)

    # --- HELPER METHODS ---

    def _get_protocol(self, key: ResourceKey) -> str:
        protocol = self._key_protocols.get(key)
        if not protocol:
            raise KeyError(f"Metadata Error: Protocol for ResourceKey '{key}' not found!")
        return protocol

    def _get_anchor(self, key: ResourceKey) -> Any:
        anchor = self._anchors.get(key)
        if anchor is None:
            raise KeyError(f"Metadata Error: Anchor for ResourceKey '{key}' not found!")
        return anchor