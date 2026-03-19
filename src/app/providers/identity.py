# src/app/providers/identity.py

from src.app.ports.input.module import AppModule
from src.app.container import ServiceContainer

# Domain Services & Models
from src.app.domain.services.resource_identity import ResourceManager, ResourceCatalog, ResourceFactory
from src.app.registry.streams import StreamRegistry
from src.app.domain.models.streams.adapter_blueprint import AdapterBlueprint
from src.app.domain.models.resource_identity import Realm

# Infrastructure: Adapters & Policies (The "Outer Ring")
from src.infrastructure.adapters.posix_file.policy import PosixFilePolicy
from src.infrastructure.adapters.posix_file.adapter import PosixFileStream
from src.infrastructure.adapters.posix_file.boundary import PosixResourceBoundary
from src.infrastructure.adapters.http.adapter import HttpStream

class IdentityModule(AppModule):
    """
    Subsystem Facade Provider: Responsible for "The What" (Resource Coordinates).
    """
    def register(self, container: ServiceContainer) -> None:
        """Phase 1: Foundations (Registry, Catalog)"""
        # 1. Initialize Foundations
        stream_registry = StreamRegistry()
        resource_catalog = ResourceCatalog()

        # 2. Map Infrastructure (The Blueprint Inventory)
        blueprints = [
            AdapterBlueprint(
                protocol="posix",
                realm=Realm.LOCAL,
                adapter_cls=PosixFileStream,
                policy=PosixFilePolicy(),
                boundary=PosixResourceBoundary()
            ),
            AdapterBlueprint(
                protocol="file",
                realm=Realm.LOCAL,
                adapter_cls=PosixFileStream,
                policy=PosixFilePolicy(),
                boundary=PosixResourceBoundary()
            ),
            AdapterBlueprint(
                protocol="http",
                realm=Realm.NETWORK,
                adapter_cls=HttpStream
            ),
            AdapterBlueprint(
                protocol="https",
                realm=Realm.NETWORK,
                adapter_cls=HttpStream
            )
        ]

        # 3. Bootstrap Registries & Catalogs
        for bp in blueprints:
            stream_registry.register(
                protocol=bp.protocol,
                realm=bp.realm,
                adapter_cls=bp.adapter_cls,
                policy=bp.policy
            )
            if bp.boundary:
                resource_catalog.register(
                    protocol=bp.protocol,
                    boundary=bp.boundary
                )
        
        # 4. Bind to Container
        container.bind(StreamRegistry, stream_registry)
        container.bind(ResourceCatalog, resource_catalog)

    def boot(self, container: ServiceContainer) -> None:
        """Phase 2: Orchestration (ResourceManager, Factory)"""
        # 1. Instantiate the Factory (The Classification Logic)
        resource_factory = ResourceFactory(
            catalog=container.get(ResourceCatalog),
            registry=container.get(StreamRegistry)
        )
        container.bind(ResourceFactory, resource_factory)

        # 2. Instantiate and Bind the ResourceManager facade
        resource_manager = ResourceManager(
            factory=resource_factory,
            catalog=container.get(ResourceCatalog),
            registry=container.get(StreamRegistry)
        )
        container.bind(ResourceManager, resource_manager)

    def teardown(self, container: ServiceContainer) -> None:
        """Clear identity caches and catalogs."""
        pass
