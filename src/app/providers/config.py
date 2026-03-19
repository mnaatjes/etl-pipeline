# src/app/providers/config.py
from src import __version__
from src.app.domain.models.app_config import AppConfig
from src.app.domain.services.session_context import SessionManager, SettingsResolver
from src.app.ports.input.module import AppModule
from src.app.container import ServiceContainer

class ConfigModule(AppModule):
    def __init__(self, overrides: dict) -> None:
        self.overrides = overrides

    def register(self, container: ServiceContainer) -> None:
        # Instantiate raw configuration dict
        config = AppConfig(**(self.overrides or {}))
        container.bind(AppConfig, config)

        # Bind Version type-var
        container.bind("api_version", __version__)

        # Bind the Settings resolver
        settings_resolver = SettingsResolver()
        container.bind(SettingsResolver, settings_resolver)

    def boot(self, container:ServiceContainer) -> None:
        """Bind Major Services from Existing Container Dependencies"""
        # Bind Session Manager
        session_service = SessionManager(
            resolver=container.get(SettingsResolver),
            app_config=container.get(AppConfig)
        )
        container.bind(SessionManager, session_service)