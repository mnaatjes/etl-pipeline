from abc import ABC, abstractmethod
from typing import Any

class StreamPolicy(ABC):
    """
    "Credential & Path Resolver." 
    - Only cares about 'where' things are ALLOWED to go; ADAPTER cares about 'how', i.e. I/O in a filesystem
    - Examples: Linux file path, a Database connection string, or an API Key for an HTTP stream
    """
    @abstractmethod
    def resolve(self, logical_uri: str) -> Any:
        """
        Translates a logical URI into the technical configuration 
        required by an adapter (e.g., Path, DSN, or API Header).
        """
        pass
    
    @abstractmethod
    def validate_access(self, resolved_config: Any) -> bool:
        """
        Pre-flight check. Does the resolved path exist? 
        Is the API key in the environment?
        """
        pass