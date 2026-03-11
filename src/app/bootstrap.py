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
from src.infrastructure.adapters.http.adapter import HttpStream

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

        # 2. REGISTRY: Central blueprint storage for Stream Adapters
        # We register 'posix' and 'file' as supported protocols for local IO.
        stream_registry = StreamRegistry()
        posix_policy = PosixFilePolicy()
        
        # Governed Protocol
        stream_registry.register(
            protocol="posix", 
            adapter_cls=PosixFileStream, 
            policy=posix_policy
        )
        
        # Direct Protocol
        stream_registry.register(
            protocol="file",
            adapter_cls=PosixFileStream,
            policy=posix_policy
        )

        # HTTP Protocols
        stream_registry.register(
            protocol="http",
            adapter_cls=HttpStream,
            policy=None
        )
        stream_registry.register(
            protocol="https",
            adapter_cls=HttpStream,
            policy=None
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

        factory = ResourceFactory(
            catalog=catalog,
            registry=stream_registry
        )

        # 4. RESOLVER: The Waterfall Engine for settings merging
        resolver = SettingsResolver()

        # 5. DEPENDENCY INJECTION: Construct the Orchestrator
        # We inject all collaborators into the StreamManager.
        return StreamManager(
            registry=stream_registry,
            factory=factory,
            catalog=catalog,
            app_config=app_config,
            resolver=resolver
        )
