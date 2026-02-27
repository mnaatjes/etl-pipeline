# src/app/bootstrap.py
from typing import Dict, Any
from dataclasses import dataclass, asdict
from src.app.ports.config import AppConfig
from src.app.ports.settings import StreamContract
from src.infrastructure.registry import StreamRegistry

class PipelineConfig:
    """
    Rules and Info
    - NOT a Singleton; Use Dependency Injection

    """

    def __init__(self, app_config: AppConfig|None = None) -> None:
        # --- Tier 1: Baseline Settings
        self.app_settings = app_config or AppConfig()

        # Internal State
        self._protocol_bootstrap: Dict[str, StreamContract] = {}

        # Factory
        # TODO: Determine Proper Method for argument injection
        self.registry = StreamRegistry(self.app_settings.chunk_size)

    def configure_protocol(self, protocol:str, settings:StreamContract) -> None:
        """Tier 2 - Bootstrap: Pre-sets behavior for a specific protocol"""
        # Validate
        if not isinstance(settings, StreamContract):
            raise TypeError(f"Settings for {protocol} MUST implement StreamContract!")
        
        # Append settings to bootstrap registry
        self._protocol_bootstrap[protocol.lower()] = settings

    def get_stream(self, uri:str, as_sink:bool=False, **overrides):
        """Public API for self.registry"""
        # Grab Protocol
        protocol = uri.split("://")[0].lower()

        # Trigger waterfall
        final_settings = self._resolve_settings(protocol, **overrides)

    def _resolve_settings(self, protocol:str, overrides: Dict[str, Any]) -> Dict[str, Any]:
        """
        Waterfall Engine
        - Tier 1: AppConfig
        - Tier 2: Bootstrap
        - Tier 3: Call Overrides
        """
        # 1. App-wide defaults
        resolved = asdict(self.app_settings)

        # 2. Protocol Specific
        if protocol in self._protocol_bootstrap:
            bootstrap_settings = asdict(self._protocol_bootstrap[protocol])
            # Update with Bootstrapped Settings
            resolved.update(bootstrap_settings)
        
        # 3. Merge with call-time overrides
        resolved.update({k: v for k,v in overrides.items() if v is not None})

        return resolved


