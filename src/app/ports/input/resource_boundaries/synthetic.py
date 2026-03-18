from .base import ResourceBoundary
from src.app.domain.models.resource_identity import SyntheticAddress, SyntheticCoordinate

class SyntheticResourceBoundary(ResourceBoundary):
    """Refined Port for anything in the SYNTHETIC realm (Procedural data)."""

    def resolve(self, address: SyntheticAddress, anchor: SyntheticCoordinate) -> SyntheticCoordinate:
        """
        Synthetic resolution logic.
        Validates generator compatibility between address and anchor.
        """
        # Synthetic resources are often 'flat'. 
        # We ensure they match the anchor's expected generator/protocol.
        if address.protocol != anchor.protocol:
             raise PermissionError(
                 f"Generator Mismatch: Address {address.protocol} != Anchor {anchor.protocol}"
             )

        # Simply promote to coordinate if protocol matches
        return SyntheticCoordinate(generator_id=address.raw_value, key=address.key)

    def is_safe(self, resource: SyntheticCoordinate, anchor: SyntheticCoordinate) -> bool:
        """Synthetic resources are safe if they match the anchored protocol."""
        return resource.protocol == anchor.protocol
