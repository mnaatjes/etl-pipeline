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
        Helper for the Adapter: 
        Ensures that if a file is Read/Write (0o664), the directory 
        is Read/Write/Execute (0o775).
        """
        return file_perms | 0o111
    
    def validate_access(self, resolved_config: Path) -> bool:
        """
        Performs the 'Pre-flight' check.
        Ensures the parent directory is at least accessible for traversal.
        """
        # List Prohibited Directories
        prohibited = ["/etc", "/root", "/boot", "/proc", "/sys"]
        path_str = str(resolved_config)

        # Perform check against prohibited directories
        if any(path_str.startswith(root) for root in prohibited):
            return False
        
        # Traversal Check
        # - Check ability to write to parent
        parent_dir = resolved_config.parent
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