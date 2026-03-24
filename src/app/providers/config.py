# src/app/providers/config.py

from dataclasses import fields
from src import __version__
from src.app.ports.input.module import AppModule
from src.app.container import ServiceContainer
from src.app.domain.models.app_config import AppConfig

class ConfigModule(AppModule):
    """
    Tier 1 Data Provider: Responsible for Global Defaults (AppConfig).
    """
    def __init__(self, overrides: dict) -> None:
        self.overrides = overrides

    def register(self, container: ServiceContainer) -> None:
        """Phase 1: Foundation (AppConfig)"""
        # 1. Filter overrides to match AppConfig fields
        valid_fields = {f.name for f in fields(AppConfig)}
        filtered = {k: v for k, v in (self.overrides or {}).items() if k in valid_fields}
        
        # 2. Instantiate and bind raw configuration
        config = AppConfig(**filtered)
        container.bind(AppConfig, config)

        # 3. Bind Version metadata
        container.bind("api_version", __version__)

    def boot(self, container: ServiceContainer) -> None:
        """Phase 2: (No-Op for Config)"""
        pass

    def teardown(self, container: ServiceContainer) -> None:
        """Cleanup config references."""
        pass
