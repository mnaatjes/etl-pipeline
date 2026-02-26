# src/infrastructure/policies/local.py
from typing import Any
from pathlib import Path
# Use the 'app' gateway
from src.app import BasePolicy

"""
Local DataStream Implementation - Filesystem - Policy / Registry
"""

class LocalFilePolicy(BasePolicy):
    def __init__(self, anchors:dict[str,str]) -> None:
        # Convert stings from config to Path objects
        # NOTE: Anchors MUST already exist in the linux filesystem; e.g. like Database and DB Tables
        self._anchors = {key: Path(val).resolve() for key, val in anchors.items()}

    def resolve(self, path: str) -> Path:
        # Collect Properties
        # - Convert input path to obj
        # - Get cwd()
        input_path   = Path(path)
        project_root = Path.cwd()

        # --- PATH A: Absolute Path Handing ---

        if input_path.is_absolute():
            # Check if full sys path
            if not str(input_path).startswith(str(project_root)):
                input_path = project_root / str(input_path).lstrip("/")

            # Locate a match
            for anchor_path in self._anchors.values():
                try:
                    # Check abs path is child of anchor
                    input_path.relative_to(anchor_path)
                    resolved = input_path.resolve()
                    return resolved
                except ValueError:
                    continue
        
        # --- PATH B: Logical Category Handling ---

        clean = path.replace("file://", "").lstrip("/")
        key, *parts = clean.split("/")
        print("\n")
        # Find path amongst anchors
        if key in self._anchors:
            anchor = self._anchors[key]
            # Strip redundant path parts: e.g. 'data/data/downloads/file.txt. --> 'data/downloads/file.txt'
            anchor_segments = list(anchor.parts)
            
            while parts and parts[0] in anchor_segments:
                parts.pop(0)

            # Use Path.resolve() to collapse any relative pathlinks '../'
            full_path = anchor.joinpath(*parts).resolve()
            print(f"Input Path: \t{str(path)}")
            print(f"Output Path: \t{full_path}")
            # GUARD: Ensure path doesn't collapse above or out of anchor
            try:
                full_path.relative_to(anchor)
                return full_path
            except:
                raise PermissionError(f"PATH TRAVERSAL! {full_path}")
            
            # full_path

        # Strict Enforcement!
        # Not in anchors is illegal operation
        raise PermissionError(
            f"Unauthorized access: Path prefix '{key}' is NOT a registered anchor"
            f"Authorized Anchors: {self.list_anchors()}"
        )

    # --- Helper Methods ---
    def has_anchor(self, key: str) -> bool:
        """Checks the internal logical registry."""
        return key in self._anchors
    
    def get_anchor_path(self, key:str) -> Path:
        if self.has_anchor(key):
            return self._anchors[key]

        raise ValueError(f"The key '{key}' is NOT Registered")
    
    def list_anchors(self) -> list[str]:
        """Returns all authorized logical keys (e.g., ['downloads', 'logs'])."""
        return list(self._anchors.keys())
    
    def list_contents(self, key: str) -> list[Path]:
        """
        Lists all files/folders inside a specific anchor.
        Useful for a pipeline to 'find' work to do.
        """
        if key not in self._anchors:
            raise KeyError(f"Anchor '{key}' not found.")
        
        anchor = self._anchors[key]
        # Uses pathlib's glob to list everything inside
        return list(anchor.iterdir())