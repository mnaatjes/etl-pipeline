# src/app/domain/services/settings_resolver.py
from typing import Any, Dict
from dataclasses import asdict
from src.app.domain.models.app_config import AppConfig

class SettingsResolver:
    """
    The 'Waterfall Engine' for Stream Configuration.
    Responsibility: Merges Global Defaults with execution-time Overrides.
    """
    @staticmethod
    def resolve(app_config:AppConfig, overrides:Dict[str, Any]) -> Dict[str,Any]:
        """
        Calculates the final - ephemeral - 'Messy Bag' of settings Dict.
        
        Tier 1: Global AppConfig (Baseline)
        Tier 3: User Overrides (Highest Priority)
        
        Note: Tier 2 (Protocol Defaults) are handled by the DataStream 
        via the dataclass default values during hydration.
        """
        # 1. Convert AppConfig to a Dict
        base_global_settings = asdict(app_config)

        # 2. Lyaer on the Overrides
        # keys in 'b' overwrite keys in 'b': {**a, **b}
        return {**base_global_settings, **overrides}