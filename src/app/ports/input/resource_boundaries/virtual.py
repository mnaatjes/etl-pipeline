from .base import ResourceBoundary
from src.app.domain.models.resource_identity import VirtualAddress, VirtualCoordinate

class VirtualResourceBoundary(ResourceBoundary):
    """Refined Port for anything in the VIRTUAL realm (Overlays/Mocking)."""

    def resolve(self, address: VirtualAddress, anchor: VirtualCoordinate) -> VirtualCoordinate:
        """
        Virtual path resolution.
        """
        # Ensure base path structure
        base_path = anchor.raw_value.rstrip("/")
        sub_path = address.parsed.path.lstrip("/")
        
        # Virtual path joining
        resolved_path = f"{base_path}/{sub_path}"

        # 1. TRAVERSAL GUARD
        if ".." in sub_path:
             raise PermissionError(f"Virtual Boundary Violation: Navigation ('..') not allowed")

        # 2. CONTAINMENT GUARD
        if not resolved_path.startswith(base_path):
             raise PermissionError(f"Virtual Boundary Violation: {resolved_path} escaped {base_path}")

        return VirtualCoordinate(virtual_path=resolved_path, key=address.key)

    def is_safe(self, resource: VirtualCoordinate, anchor: VirtualCoordinate) -> bool:
        """Checks if the virtual path is within the anchor's prefix."""
        return resource.raw_value.startswith(anchor.raw_value)
