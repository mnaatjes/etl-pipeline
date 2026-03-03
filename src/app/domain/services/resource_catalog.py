from typing import Dict, Any, TypeVar

# Updated Imports: Sourced from the new identity package
from src.app.domain.models.resource_identity import (
    ResourceKey, 
    LogicalURI, 
    PhysicalPath, 
    StreamLocation
)
from src.app.ports.input.resource_boundary import ResourceBoundary

T = TypeVar("T")

class ResourceCatalog:
    """
    The Domain Service responsible for resource discovery and security.
    Acts as the Librarian for the 'registry://' internal protocol.
    """
    def __init__(self):
        # Maps ResourceKey (e.g. "scans") -> Physical Anchor (e.g. Path("/srv/data/scans"))
        self._anchors: Dict[ResourceKey, Any] = {}
        
        # Maps Protocol String (e.g. "posix") -> ResourceBoundary Implementation
        self._boundaries: Dict[str, ResourceBoundary[Any]] = {}
        
        # Maps ResourceKey -> Protocol String
        self._key_protocols: Dict[ResourceKey, str] = {}

    def register(self, protocol: str, boundary: ResourceBoundary[Any]) -> None:
        """Registers a security guard to a specific protocol."""
        self._boundaries[protocol] = boundary

    def add_anchor(self, key: ResourceKey, protocol: str, anchor: Any) -> None:
        """Associates a nickname (key) with a protocol and a physical root."""
        if protocol not in self._boundaries:
            raise ValueError(f"No Boundary registered for protocol: {protocol}")
        
        self._anchors[key] = key
        self._key_protocols[key] = protocol

    # --- Core Logic Methods ---

    def resolve_uri(self, uri: LogicalURI) -> StreamLocation:
        """
        Translates a LogicalURI into a secured PhysicalPath (ValidatedPath).
        """
        # 1. Extract Key from the Smart Value Object
        key = ResourceKey(uri.key)

        # 2. Verified Metadata Look-ups
        protocol = self.get_protocol(key) # Promoted to public for StreamManager access
        anchor = self._get_anchor(key)
        
        # 3. Delegate to Boundary for path calculation and security checks
        boundary = self._boundaries[protocol]
        resolved_path = boundary.resolve(uri, anchor)

        # 4. BRANDING: Bind the key to the physical path before returning
        # This satisfies the ResourceIdentity contract for ValidatedPath
        if isinstance(resolved_path, PhysicalPath):
            return resolved_path.bind_key(key)
            
        return resolved_path

    # --- HELPER & METADATA METHODS ---

    def get_protocol(self, key: ResourceKey) -> str:
        """
        Returns the protocol string associated with a key.
        Promoted to public so the StreamManager can identify which Adapter to use.
        """
        protocol = self._key_protocols.get(key)
        if not protocol:
            raise KeyError(f"Metadata Error: Protocol for ResourceKey '{key}' not found!")
        return protocol

    def _get_anchor(self, key: ResourceKey) -> Any:
        """Internal helper to retrieve the physical anchor."""
        anchor = self._anchors.get(key)
        if anchor is None:
            raise KeyError(f"Metadata Error: Anchor for ResourceKey '{key}' not found!")
        return anchor