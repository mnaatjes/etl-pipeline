# src/app/ports/resolver.py

from dataclasses import asdict
from typing import Any, Dict, Optional
from src.app.ports.config import AppConfig
from src.app.ports.settings import StreamContract

class SettingsResolver:
    """Waterfall Engine: Calculates the final settings dictionary"""
    def __init__(self, app_config:AppConfig, protocol_overrides: Dict[str, StreamContract]) -> None:
        self.app_config = app_config
        self.protocol_overrides = protocol_overrides

    def resolve(self, protocol:str, call_overrides: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs the 3-Tier Waterfall Merge.
        Returns a dictionary ready for the Registry/Adapter.
        """
        # --- Tier 1: The AppConfig Baseline ---
        # We start with the 'Constitutional' defaults from AppConfig
        resolved = asdict(self.app_config)

        # --- Tier 2: The Bootstrap/Protocol Overrides ---
        # If the user pre-configured this protocol during bootstrapping
        if protocol in self.protocol_overrides:
            bootstrap_data = asdict(self.protocol_overrides[protocol])
            # We filter out None values so they don't overwrite Tier 1
            resolved.update({k: v for k, v in bootstrap_data.items() if v is not None})

        # --- Tier 3: The Call-Time Overrides ---
        # These are passed in manager.get_stream(..., timeout=5)
        # They always win.
        resolved.update({k: v for k, v in call_overrides.items() if v is not None})

        return resolved