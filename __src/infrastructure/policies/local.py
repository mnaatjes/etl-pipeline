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
        # ENFORCED: Fail-fast if anchor directory missing
        self._anchors = {}
        
        for key, val in anchors.items():
            p = Path(val).resolve()
            if not p.exists():
                raise FileNotFoundError(
                    f"FATAL: Anchor '{key}' points to non-existant directory {p}"
                    f"\nPlease create directory before initiating Local File Policy!"
                )
            
            # Assign Anchors
            self._anchors[key] = p

    def resolve(self, logical_uri: str) -> Path:
        """
        Translates a logical URI or physical path into a validated absolute Path.
        Priority:
        1. Identification: Is it already a physical path?
        2. Translation: If logical, map the key to a physical anchor.
        3. Validation: Strict boundary check (Chroot-lite).
        """
        # --- 1. Normalization ---
        # Strip protocols and leading slashes to get a clean relative-style string
        clean_path = str(logical_uri).replace("file://", "").lstrip("/")
        input_path = Path(clean_path)
        
        # --- 2. Identity Check (Idempotency) ---
        # If the input is already absolute (e.g. from a previous resolve), 
        # check if it's already safe.
        if Path(logical_uri).is_absolute():
            abs_input = Path(logical_uri)
            for anchor_path in self._anchors.values():
                try:
                    abs_input.relative_to(anchor_path)
                    return abs_input.resolve() # Already physical and authorized
                except ValueError:
                    continue

        # --- 3. Logical Mapping ---
        # Split into [key, sub_path...]
        segments = input_path.parts
        if not segments:
            raise ValueError("Empty path provided to resolve()")
            
        key = segments[0]
        remaining_parts = segments[1:]

        if key not in self._anchors:
            raise PermissionError(
                f"Unauthorized: Key '{key}' is not a registered anchor. "
                f"Available: {self.list_anchors()}"
            )

        anchor = self._anchors[key]

        # --- 4. Deduplication & Construction ---
        # Handle the case where the user repeated the anchor name in the path
        # e.g. 'data/data/logs' -> 'data/logs'
        while remaining_parts and remaining_parts[0] in anchor.parts:
            remaining_parts = remaining_parts[1:]

        # Construct the final physical path
        full_path = anchor.joinpath(*remaining_parts).resolve()

        # --- 5. Security Guard (The Sandbox) ---
        # Ensure the final path hasn't escaped the anchor via '../../'
        try:
            full_path.relative_to(anchor)
        except (ValueError, RuntimeError):
            raise PermissionError(f"PATH TRAVERSAL BLOCKED: {full_path} escapes {anchor}")

        return full_path

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