from .base import ResourceBoundary
from src.app.domain.models.resource_identity import MemoryAddress, MemoryCoordinate

class MemoryResourceBoundary(ResourceBoundary):
    """Refined Port for anything in the MEMORY realm (In-process buffers)."""

    def resolve(self, address: MemoryAddress, anchor: MemoryCoordinate) -> MemoryCoordinate:
        """
        In-memory resolution logic.
        Ensures the requested key stays within the designated pool.
        """
        base_key = anchor.raw_value
        sub_key = address.parsed.path.lstrip("/")
        
        # Ensure base ends with separator for joining
        if not base_key.endswith("/"): base_key += "/"
        resolved_key = f"{base_key}{sub_key}"

        # 1. TRAVERSAL GUARD: Ensure no '..' in memory keys
        if ".." in sub_key:
             raise PermissionError(f"Memory Boundary Violation: Navigation ('..') not allowed in memory realm")

        # 2. CONTAINMENT GUARD
        if not resolved_key.startswith(base_key):
             raise PermissionError(f"Memory Boundary Violation: {resolved_key} escaped {base_key}")

        return MemoryCoordinate(reference=resolved_key, key=address.key)

    def is_safe(self, resource: MemoryCoordinate, anchor: MemoryCoordinate) -> bool:
        """Checks if the resource key is within the anchor's prefix."""
        return resource.raw_value.startswith(anchor.raw_value)
