# src/app/bootstrap.py
from typing import Optional, Dict, Any
from src.app.domain.models.app_config import AppConfig
from src.app.domain.services.settings_resolver import SettingsResolver
from src.app.registry.streams import StreamRegistry
from src.app.use_cases.manager import StreamManager

class Bootstrap:
    """
    The 'Wiring' Logic. 
    Responsibility: Initialize and connect all application components / dependencies
    """

    @staticmethod
    def initialize(config_overrides: Optional[Dict[str, Any]] = None) -> StreamManager:
        """
        Creates:
        1. Registry
        2. Resolver
        3. Manager
        """
        # 1. SETTINGS: Initialize Global Configuration
        # TODO: call 'ConfigProvider' service to load YAML or ENV vars
        app_config = AppConfig(**(config_overrides or {}))

        # 2. REGISTRY: Init Registry and register DataStream Implementations
        registry = StreamRegistry()
        # TODO: Register Adapters
        # e.g. registry.register("https", HttpStream, HttpStreamPolicy)

        # 3. RESOLVER: Init SettingsResolver service
        resolver = SettingsResolver()

        # 4. DEPENDENCY INJECTION and INSTANTIATION
        return StreamManager(
            registry=registry,
            app_config=app_config,
            resolver=resolver
        )

