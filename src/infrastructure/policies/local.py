# src/infrastructure/policies/local.py
from typing import Any
from pathlib import Path
from ...app import BasePolicy

"""
Local DataStream Implementation - Filesystem - Policy / Registry
"""

class LocalFilePolicy(BasePolicy):
    def __init__(self, anchors:dict[str,str]) -> None:
        # Convert stings from config to Path objects
        # NOTE: Anchors MUST already exist in the linux filesystem; e.g. like Database and DB Tables
        self._anchors = {key: Path(val).resolve() for key, val in anchors.items()}

    def resolve(self, path: str) -> Path:
        clean = path.replace("file://", "").lstrip("/")
        key, *parts = clean.split("/")

        if key in self._anchors:
            anchor = self._anchors[key]
            full_path = anchor.joinpath(*parts).resolve()
        else:
            full_path = Path("/" + clean).resolve()
            # Find anchor logic...
        
        return full_path

    # --- Helper Methods ---
    def has_anchor(self, key: str) -> bool:
        """Checks the internal logical registry."""
        return key in self._anchors
    
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