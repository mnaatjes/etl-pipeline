# src/app/container.py

from typing import Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from src.app.domain.models.app_config import AppConfig

class ServiceContainer:

    def __init__(self) -> None:

        # Container
        self._services: Dict[str, Any] = {}

    def bind(self, key:str, instance:Any) -> None:
        """Stores a Service Instance (dependency) in the container"""
        self._services[key] = instance

    def get(self, key:str) -> Any:
        """Retrieves a Service"""
        instance = self._services.get(key)
        # Validate
        if instance is None:
            raise KeyError(f"Service key '{key}' not found in Container!")
        # Return stored instance
        return instance

    @property
    def settings(self) -> AppConfig:
        return self._services["settings"]