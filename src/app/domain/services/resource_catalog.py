# src/app/domain/services/resource_catalog.py
from typing import Dict, Any, TypeVar
from src.app.domain.models.types import LogicalURI, ResourceKey, ValidatedPath
from src.app.ports.input.resource_boundary import ResourceBoundary

T = TypeVar("T")

class ResourceCatalog:
    """
    The Domain Service responsible for resource discovery and security.
    Maintains the mapping of Logical Keys to Physical Anchors.
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

    def register(self, protocol:str, boundary:ResourceBoundary[Any]) -> None:
        """Registers a security guard to a specific protocol"""
        # TODO: What way is there to register or enforce list of all protocols supported
        # TODO: - Protocols align perhaps in some way with Middleware properties
        # TODO: - Get a list of ALL types in domain/models/ and look for utilization and consistencies
        # TODO: - Review if self._key_protocols is sufficient
        self._boundaries[protocol] = boundary

    def add_anchor(self, key:ResourceKey, protocol:str, anchor:Any) -> None:
        """Adds nickname (key) to catalog with its associated protocol ad physical root"""
        # Ensure protocol exists with associated boundary
        # TODO: Can we enforce types for protocol and anchor - or at least anchor (e.g. Path() for posix)
        if protocol not in self._boundaries:
            raise ValueError(f"No Boundary registered for protocol: {protocol}")
        
        # Assign anchor
        # Assign protocol
        self._anchors[key] = anchor
        self._key_protocols[key] = protocol

    def resolve_uri(self, uri:LogicalURI) -> ValidatedPath:
        """Universal resolver/translator from 'registry://path/file.xml' --> key:'path/file.xml'"""
        # 1. Parse Key
        key = self._extract_key(uri)

        # 2. Look-up Metadata
        protocol    = self._key_protocols.get(key)
        anchor      = self._anchors.get(key)
        # Ensure protocol and anchor exist
        if not protocol or not anchor:
            raise KeyError(f"Resource Key '{key}' not found in Resource Catalog!")
        
        # 3. Deligate to Boundary
        # - Boundary performs resolution based on key and protocol
        boundary = self._boundaries[protocol]

        # 4. Grab physical - resolved path - and return ValidatedPath
        return ValidatedPath(boundary.resolve(uri, anchor))

    def _extract_key(self, uri:LogicalURI) -> ResourceKey:
        """Helper pulls anchor key from logical string"""
        # Cast as string
        uri_str = str(uri)

        # 1. Enforce Scheme (://)
        if "://" not in uri_str:
            raise ValueError(f"Malformed LogicalURI: Missing scheme (e.g. registry://) in '{uri_str}'")

        # 2. Extract the part after scheme
        path_part = uri_str.split("://")[-1]

        # 3. Extract Key
        key = path_part.split("/")[0]

        # 4. Enforce key not empty
        if not key:
            raise ValueError(f"Malformed LogicalURI: Resource Key CANNOT be empty in '{uri_str}'")
        
        # 5. Make ResourceKey and return
        return ResourceKey(key)