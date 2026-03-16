# src/app/providers/config.py
from typing import NewType
from src import __version__
from src.app.domain.models.app_config import AppConfig
from src.app.ports.input.module import AppModule
from src.app.container import ServiceContainer

class ConfigModule(AppModule):
    def __init__(self, overrides: dict) -> None:
        self.overrides = overrides

    def register(self, container: ServiceContainer) -> None:
        # Instantiate raw configuration module
        config = AppConfig(**(self.overrides or {}))
        container.bind(AppConfig, config)

        # Bind Version type-var
        container.bind("api_version", __version__)

    def boot(self, container:ServiceContainer) -> None:
        pass