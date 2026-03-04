# src/infrastructure/adapters/posix_file/policy.py
import os
from pathlib import Path
from typing import Any

from src.app.ports.output.stream_policy import StreamPolicy
from src.infrastructure.adapters.posix_file.contract import PosixFileContract, FileReadMode

class PosixFilePolicy(StreamPolicy):
    """
    Governance for POSIX (Linux) Filesystem Operations
    """
    def derive_dir_permissions(self, file_perms:int) -> int:
        """
        Calculates directory permissions based on file permissions.
        Ensures 'Execute' bits are set so the OS can traverse the path.
        
        Logic: For every 'Read' bit (4), add an 'Execute' bit (1).
        Example: 0o664 (rw-rw-r--) -> 0o775 (rwxrwxr-x)
        """
        # Start with the base file permissions
        dir_perms = file_perms

        # If User can read, User must execute
        if file_perms & 0o400: dir_perms |= 0o100
        # If Group can read, Group must execute
        if file_perms & 0o040: dir_perms |= 0o010
        # If Others can read, Others must execute
        if file_perms & 0o004: dir_perms |= 0o001

        return dir_perms
    
    def validate_access(self, resolved_config: Any) -> bool:
        """
        Performs the 'Pre-flight' check.
        Ensures the parent directory is at least accessible for traversal.
        """
        from src.app.domain.models.resource_identity import PhysicalURI

        # 1. Promote to Path object
        if isinstance(resolved_config, PhysicalURI):
            if resolved_config.protocol != "file":
                # Only 'file' is safe to promote to a local path
                return False
            path_obj = Path(resolved_config.split("://")[1])
        else:
            path_obj = Path(resolved_config)

        # 2. List Prohibited Directories
        prohibited = ["/etc", "/root", "/boot", "/proc", "/sys"]
        path_str = str(path_obj)

        # 3. Perform check against prohibited directories
        if any(path_str.startswith(root) for root in prohibited):
            return False
        
        # 4. Traversal Check
        # - Check ability to write to parent
        parent_dir = path_obj.parent
        if parent_dir.exists():
            return os.access(parent_dir, os.X_OK)
        
        # Parent does NOT exist
        # - Creation handled by Adapter
        return True

    def resolve(self, logical_uri:str) -> Path:
        """
        Translates a string path into a technical Path object.
        Handles expansion of home directories (~) for the 'hp_prodesk' user.
        """
        return Path(logical_uri).expanduser().resolve()
    
    def validate_path_safety(self, uri:str) -> None:
        pass