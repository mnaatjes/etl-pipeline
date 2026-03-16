# src/app/ports/input/module.py

from abc import ABC, abstractmethod
from src.app.container import ServiceContainer

class AppModule(ABC):

    @abstractmethod
    def register(self, container: 'ServiceContainer'):
        """Phase 1: Create Raw Dependency"""
        pass

    @abstractmethod
    def boot(self, container: 'ServiceContainer'):
        """Phase 2: Wire complex dependencies"""
        pass