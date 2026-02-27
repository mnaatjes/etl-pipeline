# Implementation: Settings Resolution (The Waterfall)

The `SettingsResolver` is the "Logic Tool" that calculates the final configuration for any given stream based on a 3-tier merging strategy.

## The 3-Tier Waterfall Merge

1.  **Tier 1: App Defaults:** Global settings defined in `AppConfig` (e.g., `default_chunk_size`).
2.  **Tier 2: Bootstrap Protocol Overrides:** Settings provided during the bootstrap phase for a specific protocol (e.g., `HttpSettings(retries=5)`).
3.  **Tier 3: Call-time Overrides:** Specific arguments passed directly to `get_stream()` (e.g., `manager.get_stream(uri, timeout=300.0)`).

## SettingsResolver Implementation

```python
from dataclasses import asdict
from typing import Any, Dict
from src.app.ports.config import AppConfig

class SettingsResolver:
    """SRP: Only handles the logic of merging settings Tiers."""
    def __init__(self, app_config: AppConfig, protocol_overrides: Dict[str, Any]):
        self.app_config = app_config
        self.protocol_overrides = protocol_overrides

    def resolve(self, protocol: str, call_overrides: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates the Tier 1 -> Tier 2 -> Tier 3 Waterfall merge."""
        
        # 1. Tier 1: App-wide defaults
        resolved = {
            "chunk_size": self.app_config.default_chunk_size,
            "use_lines": False  # Absolute fallback
        }

        # 2. Tier 2: Bootstrap/Protocol Level
        if protocol in self.protocol_overrides:
            bootstrap_data = asdict(self.protocol_overrides[protocol])
            # Filter out Nones to allow Tier 1 to shine through
            resolved.update({k: v for k, v in bootstrap_data.items() if v is not None})

        # 3. Tier 3: Call-time Overrides
        # This always wins for the specific instance.
        resolved.update({k: v for k, v in call_overrides.items() if v is not None})

        return resolved
```

## Immutability and State Pollution
By using this pattern, the global "Regime" held by the `StreamManager` remains immutable. Call-time overrides only affect the specific `DataStream` instance being created. This prevents "State Pollution" where a one-off change accidentally affects all future stream operations.
