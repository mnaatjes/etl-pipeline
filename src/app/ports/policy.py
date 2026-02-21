# src/app/ports/policy.py

from abc import ABC, abstractmethod
from typing import Any

class BasePolicy(ABC):
    """
    "Credential & Path Resolver." 
    Whether it's a Linux file path, a Database connection string, or an API Key for an HTTP stream, 
    every adapter needs to translate a Logical URI (the "What") into Physical Configuration (the "How")
    """
    @abstractmethod
    def resolve(self, logical_uri: str) -> Any:
        """
        Translates a logical URI into the technical configuration 
        required by an adapter (e.g., Path, DSN, or API Header).
        """
        pass