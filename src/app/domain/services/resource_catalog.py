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
        # Maps a ResourceKey (e.g. "downloads") to a physical Anchor (e.g. Path())
        self._anchors: Dict[ResourceKey, Any] = {}
        # Maps a Protocol (e.g. posix) to its specific ResourceBoundary implementation
        self._boundaries: Dict[str, ResourceBoundary[Any]] = {}
        # Maps a ResourceKey to its Protocol Type
        self._key_protocols: Dict[ResourceKey, str] = {}