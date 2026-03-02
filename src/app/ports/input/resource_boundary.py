# src/app/ports/input/resource_boundary.py

from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from src.app.domain.models.types import LogicalURI, ValidatedPath

# T is the "Physical" result (e.g. Path() for files, DSN for Databases)
T = TypeVar("T")

class ResourceBoundary(ABC, Generic[T]):
    """
    Abstract Input Port for Resource Security
    - Ensures logical requests cannot 'escape' boundaries
    - Aids in uri resolution
    """
    @abstractmethod
    def resolve(self, uri:LogicalURI, anchor:T) -> T:
        """
        Translates a logical string-based URI into a concrete physical resource.
        - Strips logical prefixes (e.g., registry://)
        - Joins the sub-path to the anchor
        - Performs normalization (resolving '..' or '.' segments)

        Args:
            uri (LogicalURI): The raw, untrusted logical string provided 
                by the user or configuration (e.g., "registry://scans/01.xml").
            anchor (T): The physical 'root' or 'home' directory that acts as 
                the cage for this specific resource key (e.g., Path("/srv/data")).

        Returns:
            T: The resolved physical resource (e.g., a pathlib.Path object).
        
        Raises:
            PermissionError: If the resolved path attempts to escape the anchor.
            ValueError: If the URI format is malformed or invalid for this boundary.
        """
        pass

    @abstractmethod
    def is_safe(self, physical_resource:T, anchor:T) -> bool:
        """
        Performs the final validation check to ensure boundary containment.

        - Compares the resolved physical resource against the anchor to ensure no 'escape' has occurred
        - Ensures symbolic links, path traversal, or logic errors cannot occur

        Args:
            physical_resource (T): The concrete resource to validate 
                (e.g., Path("/srv/data/scans/file.xml")).
            anchor (T): The authorized root container 
                (e.g., Path("/srv/data")).

        Returns:
            bool: True if the resource is strictly contained within or equal 
                to the anchor; False if it resides outside the boundary.
        """
        pass