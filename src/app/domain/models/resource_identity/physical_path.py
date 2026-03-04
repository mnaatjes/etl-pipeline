# src/app/domain/models/resource_identity/physical_path.py
import os
from pathlib import Path, PosixPath, WindowsPath
from src.app.domain.models.resource_identity.base import ResourceIdentity
from src.app.domain.models.resource_identity.types import ResourceKey

class PhysicalPath(Path, ResourceIdentity):
    """
    A local path that has been vetted by a ResourceBoundary.
    Uses the pathlib factory pattern to ensure isinstance() works 
    across different operating systems.
    """
    def __new__(cls, *args, **kwargs):
        if cls is PhysicalPath:
            # Dynamically route to the correct OS-specific subclass
            cls = PosixPhysicalPath if os.name == 'posix' else WindowsPhysicalPath
        return super().__new__(cls, *args, **kwargs)

    # Note: Because Path is immutable, we attach the key after resolution.
    _key: ResourceKey

    @property
    def key(self) -> ResourceKey:
        """The logical identifier used for cataloging."""
        return getattr(self, "_key", None)

    def bind_key(self, key: ResourceKey) -> "PhysicalPath":
        """Attaches the logical key to this physical path coordinate."""
        self._key = key
        return self

class PosixPhysicalPath(PosixPath, PhysicalPath):
    """Linux/Unix specific implementation of PhysicalPath."""
    pass

class WindowsPhysicalPath(WindowsPath, PhysicalPath):
    """Windows specific implementation of PhysicalPath."""
    pass
