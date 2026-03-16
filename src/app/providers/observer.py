#

from src.app.ports.input.module import AppModule
from src.app.container import ServiceContainer
from src.app.domain.services.traceability_provider import TraceabilityProvider

class ObserverModule(AppModule):

    def register(self, container: ServiceContainer) -> None:
        container.bind(
            key=TraceabilityProvider,
            instance=TraceabilityProvider()
        )

    def boot(self, container: ServiceContainer) -> None:
        pass