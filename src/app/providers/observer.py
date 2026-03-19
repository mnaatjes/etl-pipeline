# src/app/providers/observer.py

from src.app.ports.input.module import AppModule
from src.app.container import ServiceContainer

class ObserverModule(AppModule):
    """
    Reserved for future implementation of:
    - Event Bus / Notifications
    - Telemetry / Logging Adapters
    - Stream Observation Hooks
    """
    def register(self, container: ServiceContainer) -> None:
        pass

    def boot(self, container: ServiceContainer) -> None:
        pass

    def teardown(self, container: ServiceContainer) -> None:
        """Unregister listeners or observers."""
        pass
