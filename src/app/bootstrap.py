# src/app/bootstrap.py
from typing import Optional, Dict, Any
from src.app.domain.models.app_config import AppConfig
from src.app.domain.services.settings_resolver import SettingsResolver
from src.app.domain.services.resource_catalog import ResourceCatalog
from src.app.domain.services.resource_factory import ResourceFactory
from src.app.registry.streams import StreamRegistry
from src.app.use_cases.manager import StreamManager

# Infrastructure Imports
from src.infrastructure.adapters.posix_file.adapter import PosixFileStream
from src.infrastructure.adapters.posix_file.boundary import PosixResourceBoundary
from src.infrastructure.adapters.posix_file.policy import PosixFilePolicy

class Bootstrap:
    """
    The 'Wiring' Logic. 
    Responsibility: Initialize and connect all application components / dependencies.
    Acts as the Composition Root for the application.
    """

    @staticmethod
    def initialize(config_overrides: Optional[Dict[str, Any]] = None) -> StreamManager:
        """
        Orchestrates the creation and injection of all core services.
        """
        # 1. SETTINGS: Initialize Global Configuration
        # TODO: Integrate a 'ConfigProvider' for YAML/ENV loading
        app_config = AppConfig(**(config_overrides or {}))

        # 2. REGISTRY: Central blueprint storage for Adapters
        # We register 'posix' as a supported protocol.
        registry = StreamRegistry()
        posix_policy = PosixFilePolicy()
        registry.register(
            protocol="posix", 
            adapter_cls=PosixFileStream, 
            policy=posix_policy
        )
        
        # 3. RESOURCE SERVICES: The High-Resolution Identity Stack
        # - Catalog: Stores internal keys and their physical anchors
        # - Factory: Promotes strings to StreamLocation objects
        catalog = ResourceCatalog()
        
        # Register the Boundary for the 'posix' protocol
        catalog.register(
            protocol="posix", 
            boundary=PosixResourceBoundary()
        )

        factory = ResourceFactory(catalog=catalog)

        # 4. RESOLVER: The Waterfall Engine for settings merging
        resolver = SettingsResolver()

        # 5. DEPENDENCY INJECTION: Construct the Orchestrator
        # We inject all collaborators into the StreamManager.
        return StreamManager(
            registry=registry,
            factory=factory,
            catalog=catalog,
            app_config=app_config,
            resolver=resolver
        )
