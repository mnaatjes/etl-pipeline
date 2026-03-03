# src/app/ports/input/resource_boundary.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

# Updated Imports: Utilizing the high-fidelity identity suite
from src.app.domain.models.resource_identity import LogicalURI, PhysicalPath

# T represents the "Anchor Type" (the root cage).
# For POSIX, T is pathlib.Path. For HTTP, T is often a str.
T = TypeVar("T")

class ResourceBoundary(ABC, Generic[T]):
    """
    Abstract Input Port for Resource Security and Boundary Enforcement.
    
    Responsibilities:
    - Acts as the 'Chroot-lite' for the domain, preventing directory traversal.
    - Bridges the gap between a 'LogicalURI' (Intent) and 'PhysicalPath' (Reality).
    - Enforces the 'Security Cage' (Anchor) for every governed resource.
    
    Hexagonal Role:
    This is an Input Port (Primary Port). It defines the contract that 
    infrastructure-specific guards (like PosixResourceBoundary) must fulfill.
    """

    @abstractmethod
    def resolve(self, uri: LogicalURI, anchor: T) -> PhysicalPath:
        """
        Translates a logical identity into a concrete, secured PhysicalPath.

        Internal Logic Steps for Implementations:
        1. Parse the sub-path from the LogicalURI (path_remainder).
        2. Combine the sub-path with the physical anchor (T).
        3. Normalize the resulting path (stripping '..' and symbols).
        4. Validate safety via `is_safe()` before returning.

        Args:
            uri (LogicalURI): The smart Value Object representing a 'registry://' 
                identity (e.g., registry://scans/01.xml).
            anchor (T): The physical 'home' or 'root' coordinate that serves as 
                the boundary (e.g., Path("/srv/data/scans")).

        Returns:
            PhysicalPath: A fully-realized, secured physical path object 
                branded with its identity metadata.
        
        Raises:
            PermissionError: If the resolved path attempts to escape the anchor 
                (e.g., via '../' traversal).
            ValueError: If the URI sub-path format is invalid for this boundary.
        """
        pass

    @abstractmethod
    def is_safe(self, physical_resource: PhysicalPath, anchor: T) -> bool:
        """
        The final integrity check for boundary containment.

        - Compares the resolved resource against the anchor.
        - Verifies that the resource is 'under' the anchor in the hierarchy.
        - Mitigates symbolic link attacks or 'breakout' attempts.

        Args:
            physical_resource (PhysicalPath): The concrete path produced during 
                resolution (e.g., /srv/data/scans/file.xml).
            anchor (T): The authorized root container (e.g., /srv/data/scans).

        Returns:
            bool: True if the resource is strictly contained within the anchor's 
                namespace; False otherwise.
        """
        pass