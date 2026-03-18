# src/app/ports/input/resource_boundaries/base.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from src.app.domain.models.resource_identity import Address, Coordinate

class ResourceBoundary(ABC):
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
    def resolve(self, address: Address, anchor: Coordinate) -> Coordinate:
        """
        Translates an Address (intent) into a secured Coordinate (reality)

        Args: 
            address (Address): e.g. 'registry://scans/01.csv
            anchor (Coordinate): Authorized 'cage' root; e.g. '/src/data/path'
        """
        pass

    @abstractmethod
    def is_safe(self, resource: Coordinate, anchor: Coordinate) -> bool:
        """
        Final containment check. Ensures 'resource' is under 'anchor'
        """
        pass