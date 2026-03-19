# src/app/providers/streams.py

from src.app.ports.input.module import AppModule
from src.app.container import ServiceContainer

# Facades
from src.app.domain.services.resource_identity import ResourceManager
from src.app.domain.services.session_context import SessionManager
from src.app.use_cases.manager import StreamManager

class StreamModule(AppModule):
    """
    Gateway Provider: Responsible for the "Gateway" (StreamManager).
    """
    def register(self, container: ServiceContainer) -> None:
        """Phase 1: (No-Op for Streams)"""
        pass

    def boot(self, container: ServiceContainer) -> None:
        """Phase 2: Orchestration (StreamManager)"""
        # 1. Instantiate and bind the StreamManager gateway
        # Note: Depends on both ResourceManager and SessionManager facades
        manager = StreamManager(
            resource_manager=container.get(ResourceManager),
            session_manager=container.get(SessionManager)
        )
        container.bind(StreamManager, manager)

    def teardown(self, container: ServiceContainer) -> None:
        """Force close any dangling stream handles."""
        pass
