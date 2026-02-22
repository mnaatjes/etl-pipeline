# /srv/pipeline/src/app/ports/middleware.py

from abc import ABC, abstractmethod
from typing import Any

class Middleware(ABC):
    """The absolute base for all pipeline processors."""
    @abstractmethod
    def __call__(self, item: Any) -> Any:
        pass

class ByteMiddleware(Middleware):
    """Contract: Input and Output must be bytes."""
    def __call__(self, item: Any) -> bytes:
        if not isinstance(item, (bytes, bytearray)):
            raise TypeError(f"{self.__class__.__name__} expects bytes, got {type(item).__name__}")
        return self.process(item)

    @abstractmethod
    def process(self, item: bytes) -> bytes:
        pass

class ObjectMiddleware(Middleware):
    """Contract: Input and Output must be structured (dicts/lists)."""
    def __call__(self, item: Any) -> dict | list:
        if not isinstance(item, (dict, list)):
            raise TypeError(f"{self.__class__.__name__} expects dict/list, got {type(item).__name__}")
        return self.process(item)

    @abstractmethod
    def process(self, item: dict | list) -> dict | list:
        pass