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
        if not self.is_safe(LocalCoordinate(path=str(candidate)), anchor):
            raise PermissionError(f"Boundary Violation! {candidate} escaped {anchor_root}")
    
        # 4. PROMOTE: Use the address key to maintain identity
        return LocalCoordinate(path=str(candidate), key=address.key)
    
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
