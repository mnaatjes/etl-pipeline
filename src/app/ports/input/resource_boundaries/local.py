from abc import abstractmethod
from .base import ResourceBoundary
from src.app.domain.models.resource_identity import LocalAddress, LocalCoordinate

class LocalResourceBoundary(ResourceBoundary):
    """Refined Port for anything in the LOCAL realm (POSIX, Windows, etc)."""
    
    def resolve(self, address: LocalAddress, anchor: LocalCoordinate) -> LocalCoordinate:
        """
        Concrete Guardian Logic: Uniform for all Local Filesystems.
        Prevents absolute path injection and directory traversal at the domain level.
        """
        # 1. DOMAIN SANITIZATION
        # Strip leading separators to ensure it's treated as a relative subpath.
        raw_subpath = address.parsed.path
        clean_subpath = raw_subpath.lstrip("/")

        # 2. ABSOLUTE INJECTION GUARD
        # Reject if the remaining path is STILL in an absolute format.
        # e.g., registry://scans//etc/passwd -> clean = /etc/passwd -> FAIL
        # e.g., registry://scans/C:/win -> clean = C:/win -> FAIL
        if self._is_absolute_format(clean_subpath):
             raise PermissionError(f"Boundary Violation: Absolute path injection detected: {clean_subpath}")

        # 3. DELEGATE REALITY (Infrastructure Math)
        return self._do_resolve(clean_subpath, anchor, address)

    @abstractmethod
    def _do_resolve(self, subpath: str, anchor: LocalCoordinate, address: LocalAddress) -> LocalCoordinate:
        """
        The 'Bridge' to Infrastructure. 
        Implemented by PosixResourceBoundary or WindowsResourceBoundary.
        """
        pass

    @abstractmethod
    def is_safe(self, resource: LocalCoordinate, anchor: LocalCoordinate) -> bool:
        """
        Final containment check. 
        Must be implementation-specific to handle Symlink resolution (TOCTOU).
        """
        pass

    def _is_absolute_format(self, path: str) -> bool:
        """Domain-level check for path structure without using OS modules."""
        # Check for / (Unix) or C: (Windows)
        return path.startswith("/") or (len(path) > 1 and path[1] == ":")
