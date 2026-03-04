# src/app/stream_client.py

from typing import Any, Optional, Dict

class StreamClient:
    """
    The Public Facade for the StreamFlow Framework.
    User's single point of entry for all DataStream operations.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initializes the internal engine via the Bootstrap.
        :param config: Tier 1 (Global) overrides (e.g., from a YAML loader).
        """
        # Move import inside to break circular dependency
        from src.app.bootstrap import Bootstrap
        
        # The 'Big Bang': Manager, Registry, and Resolver are wired here.
        self._manager = Bootstrap.initialize(config_overrides=config)

    def get_handle(
        self, 
        uri: str, 
        as_sink: bool = False, 
        **settings
    ) -> Any:
        """
        Requests a Smart Handle from the Orchestrator.
        """
        return self._manager.get_handle(uri, as_sink=as_sink, **settings)

    def read(self, uri: str) -> Any:
        """Convenience: Read entire stream contents as Packets."""
        return self._manager.read(uri)

    def write(self, uri: str, data: Any) -> None:
        """Convenience: Write data to a stream via a Packet."""
        self._manager.write(uri, data)

    def exists(self, uri: str) -> bool:
        """Convenience: Check resource existence."""
        return self._manager.exists(uri)

    def resolve(self, uri: str) -> Any:
        """
        Resolves a URI to its physical location (Path or URL).
        """
        return self._manager.resolve(uri)

    def add_resource(self, key: str, protocol: str, anchor: Any) -> None:
        """
        Registers a physical resource (e.g., a local directory or S3 bucket) 
        under a logical name (key).
        """
        self._manager.add_resource(key, protocol, anchor)
