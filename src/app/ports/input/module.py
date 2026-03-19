# src/app/ports/input/module.py

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app.container import ServiceContainer

class AppModule(ABC):
    """
    Abstract Base Class for Service Providers (Modules).
    
    Modules are responsible for the two-phase lifecycle of the ServiceContainer:
    1. Register: Bind foundations and raw types.
    2. Boot: Instantiate and wire complex facades and managers.
    3. Teardown: (Optional) Graceful release of resources.
    """
    
    @property
    def name(self) -> str:
        """Returns the name of the module for logging and debugging."""
        return self.__class__.__name__

    @abstractmethod
    def register(self, container: 'ServiceContainer') -> None:
        """Phase 1: Foundation. Bind raw types and registries."""
        pass

    @abstractmethod
    def boot(self, container: 'ServiceContainer') -> None:
        """Phase 2: Orchestration. Wire complex facades and managers."""
        pass

    def teardown(self, container: 'ServiceContainer') -> None:
        """Optional: Graceful shutdown logic (default is No-Op)."""
        pass
