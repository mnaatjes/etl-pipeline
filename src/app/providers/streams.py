# src/app/providers/streams.py

from src.app.container import ServiceContainer
from src.app.ports.input.module import AppModule

# Resources
from src.app.registry.streams import StreamRegistry
from src.app.domain.services.resource_catalog import ResourceCatalog
from src.app.domain.services.settings_resolver import SettingsResolver
from src.app.domain.models.streams.adapter_blueprint import AdapterBlueprint
from src.app.domain.services.resource_factory import ResourceFactory
from src.app.use_cases.manager import StreamManager

# Policies, Adapters, Boundaries, etc
from src.infrastructure.adapters.posix_file.policy import PosixFilePolicy
from src.infrastructure.adapters.posix_file.adapter import PosixFileStream
from src.infrastructure.adapters.posix_file.boundary import PosixResourceBoundary
from src.infrastructure.adapters.http.adapter import HttpStream

class StreamModule(AppModule):
    """
    Core I/O Module Responsible for:
    - Resource Identity
    - Registry of Adapters
    - StreamManager
    """
    def register(self, container: ServiceContainer) -> None:
        """Phase 1: Registries, Catalogs, Resolvers"""
        
        # Initialize Foundation
        stream_registry = StreamRegistry()
        resource_catalog = ResourceCatalog()

        # Describe the Infrastructure Map
        blueprints = [
            AdapterBlueprint(
                protocol="posix",
                adapter_cls=PosixFileStream,
                policy=PosixFilePolicy(),
                boundary=PosixResourceBoundary()
            ),
            AdapterBlueprint(
                protocol="file",
                adapter_cls=PosixFileStream,
                policy=PosixFilePolicy(),
                boundary=PosixResourceBoundary()
            ),
            AdapterBlueprint(
                protocol="http",
                adapter_cls=HttpStream
            ),
            AdapterBlueprint(
                protocol="https",
                adapter_cls=HttpStream
            )
        ]

        # Bootstrap Blueprints
        for bp in blueprints:
            # Add to StreamRegistry
            stream_registry.register(
                protocol=bp.protocol,
                adapter_cls=bp.adapter_cls,
                policy=bp.policy
            )

            # Add to catalog if ResourceBoundary is set
            if bp.boundary:
                resource_catalog.register(
                    protocol=bp.protocol,
                    boundary=bp.boundary
                )
        
        # Bind Foundations
        container.bind(
            key=StreamRegistry,
            instance=stream_registry
        )
        container.bind(
            key=ResourceCatalog,
            instance=resource_catalog
        )

        # Bind Settings Resolver Service
        container.bind(SettingsResolver, SettingsResolver())

    
    def boot(self, container:ServiceContainer) -> None:
        """Phase 2: Orchestration"""

        # 1. Resource Factory
        resource_factory = ResourceFactory(
            catalog=container.get(ResourceCatalog),
            registry=container.get(StreamRegistry)
        )

        # 2. Instantiate and Bind StreamManager
        manager = StreamManager(
            registry=container.get(StreamRegistry),
            factory=resource_factory,
            catalog=container.get(ResourceCatalog),
            app_config=container.settings,
            resolver=container.get(SettingsResolver)
        )

        # Bind StreamManager
        container.bind(StreamManager, manager)