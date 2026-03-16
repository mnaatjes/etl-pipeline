# src/app/bootstrap.py

# Frameworks and Libraries
from typing import Dict

# Application Foundation
from src.app.container import ServiceContainer

# Modules
from src.app.providers.config import ConfigModule
from src.app.providers.observer import ObserverModule
from src.app.providers.streams import StreamModule
from src.app.providers.pipeline import PipelineModule

class Bootstrap:
    """

    """
    @staticmethod
    def initialize(overrides:Dict={}) -> ServiceContainer:
        """
        - Define list of modules
        - Registration
        - Booting
        """
        # 0. Instantiate Container
        container = ServiceContainer()

        # 1. DEFINE Modules to be registered and booted
        modules = [
            ConfigModule(overrides),
            ObserverModule(),
            StreamModule(),
            PipelineModule()
        ]

        # 2. REGISTER
        for m in modules:
            m.register(container)

        # 3. BOOT
        for m in modules:
            m.boot(container)

        # Return Completed Container
        return container
    
    @staticmethod
    def teardown() -> None:
        pass

    @staticmethod
    def reinitialize() -> None:
        pass