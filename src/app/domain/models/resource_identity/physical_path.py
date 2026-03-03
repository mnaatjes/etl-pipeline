# src/app/domain/models/resource_identity/physical_path.py
from pathlib import Path
from src.app.domain.models.resource_identity.base import ResourceIdentity
from src.app.domain.models.resource_identity.types import ResourceKey

class PhysicalPath(Path, ResourceIdentity):
    """
    A local path that has been vetted by a ResourceBoundary.
    Inherits from Path to allow: with validated_path.open() as f:
    """
    # Note: Because Path is immutable and uses __new__, 
    # we use a helper to attach the key after resolution.
    _key: ResourceKey

    @property
    def key(self) -> ResourceKey:
        return self._key

    def bind_key(self, key: ResourceKey) -> "PhysicalPath":
        """Attaches the logical key to this physical path."""
        self._key = key
        return self