# src/app/providers/session.py

from src.app.ports.input.module import AppModule
from src.app.container import ServiceContainer

# Domain Services
from src.app.domain.services.session_context import SessionManager, SettingsResolver, TraceabilityProvider
from src.app.domain.models.app_config import AppConfig

class SessionModule(AppModule):
    """
    Subsystem Facade Provider: Responsible for the "Passport" (SessionContext).
    """
    def register(self, container: ServiceContainer) -> None:
        """Phase 1: Foundations (Traceability, Resolver)"""
        # 1. Bind the Traceability Provider (ID Generator)
        container.bind(TraceabilityProvider, TraceabilityProvider())

        # 2. Bind the Settings Resolver (The Waterfall Engine)
        # This is the single source of truth for settings merging.
        container.bind(SettingsResolver, SettingsResolver())

    def boot(self, container: ServiceContainer) -> None:
        """Phase 2: Orchestration (SessionManager)"""
        # 1. Instantiate and bind the SessionManager facade
        manager = SessionManager(
            resolver=container.get(SettingsResolver),
            app_config=container.get(AppConfig)
        )
        container.bind(SessionManager, manager)

    def teardown(self, container: ServiceContainer) -> None:
        """Reset session context and clear trace IDs."""
        pass
