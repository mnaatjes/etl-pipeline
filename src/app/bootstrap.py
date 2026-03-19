# src/app/bootstrap.py

# Frameworks and Libraries
from typing import Dict, List

# Application Foundation
from src.app.container import ServiceContainer
from src.app.ports.input.module import AppModule

# Modules
from src.app.providers.config import ConfigModule
from src.app.providers.session import SessionModule
from src.app.providers.identity import IdentityModule
from src.app.providers.observer import ObserverModule
from src.app.providers.streams import StreamModule
from src.app.providers.pipeline import PipelineModule

class Bootstrap:
    """
    Composition Root: Responsible for Orchestrating the ServiceContainer.
    """
    
    # Track modules for teardown
    _modules: List[AppModule] = []

    @classmethod
    def initialize(cls, overrides:Dict={}) -> ServiceContainer:
        """
        - Define list of modules
        - Registration (Phase 1)
        - Booting (Phase 2)
        """
        # 0. Instantiate Container
        container = ServiceContainer()

        # 1. DEFINE Specialized Modules in order of dependency
        cls._modules = [
            ConfigModule(overrides),    # Level 0: Foundations (Data)
            SessionModule(),           # Level 1: Domain Services (Who/How)
            IdentityModule(),          # Level 1: Domain Services (What)
            ObserverModule(),          # Level 2: Observability (Events)
            StreamModule(),            # Level 3: Use Cases (The Gateway)
            PipelineModule()           # Level 4: Workflows (The Engine)
        ]

        # 2. REGISTER (Phase 1: Foundations)
        for m in cls._modules:
            m.register(container)

        # 3. BOOT (Phase 2: Orchestration)
        for m in cls._modules:
            m.boot(container)

        # Return Completed Container
        return container
    
    @classmethod
    def teardown(cls, container: ServiceContainer) -> None:
        """
        Gracefully shut down all modules in reverse order.
        """
        # Teardown in reverse order of initialization
        for m in reversed(cls._modules):
            m.teardown(container)
        
        # Clear module tracking
        cls._modules = []

    @staticmethod
    def reinitialize() -> None:
        """Deprecated: Use teardown + initialize instead."""
        pass
