# src/infrastructure/adapters/posix_file/boundary.py
from pathlib import Path
from src.app.ports.input.resource_boundaries import LocalResourceBoundary
from src.app.domain.models.resource_identity import LocalAddress, LocalCoordinate

class PosixResourceBoundary(LocalResourceBoundary):
    """
    POSIX Implementation of the Local Resource Boundary.
    Uses pathlib for cross-platform path joining and physical resolution.
    """

    def _do_resolve(self, subpath: str, anchor: LocalCoordinate, address: LocalAddress) -> LocalCoordinate:
        """
        The POSIX-specific mechanical path joining.
        """
        # 1. STANDARDIZE anchor (Ensure it is a real physical path)
        anchor_root = Path(anchor.raw_value).resolve()

        # 2. RESOLVE candidate
        # Subpath is already 'clean' from the Port's resolve()
        candidate = (anchor_root / subpath).resolve()

        # 3. VERIFY (Final safety check using physical resolution)
        # Pass the protocol metadata so the registry lookup continues to work
        candidate_coord = LocalCoordinate(path=str(candidate), protocol=address.protocol)
        if not self.is_safe(candidate_coord, anchor):
            raise PermissionError(f"Boundary Violation! {candidate} escaped {anchor_root}")
    
        # 4. PROMOTE: Reconstruct Coordinate with original key and protocol
        return LocalCoordinate(path=str(candidate), protocol=address.protocol, key=address.key)
    
    def is_safe(self, resource: LocalCoordinate, anchor: LocalCoordinate) -> bool:
        """
        Physical safety check: Handles symlinks and directory traversal.
        """
        resolved_path = Path(resource.raw_value).resolve()
        anchor_path   = Path(anchor.raw_value).resolve()
        
        try:
            # relative_to raises ValueError if path is not under anchor
            resolved_path.relative_to(anchor_path)
            return True
        except ValueError:
            return False
