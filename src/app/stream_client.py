# src/app/stream_client.py

from typing import Any, Optional, Dict

from src.app.domain.models.resource_identity import StreamLocation
from src.app.domain.services.traceability_provider import TraceabilityProvider

class StreamClient:
    """
    The Public Facade for the StreamFlow Framework.
    User's single point of entry for all DataStream operations.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None, trace_id:Optional[str] = None):
        """
        Initializes the internal engine via the Bootstrap.
        :param config: Tier 1 (Global) overrides (e.g., from a YAML loader).
        :param trace_id: Optional Session/Trace id
        """
        # Extract the configs
        config_bag = config or {}
        # Extract trace_id
        provided_id = trace_id or config_bag.get("trace_id", None)

        # 1. RESOLVE TRACE
        self._trace_id = TraceabilityProvider.resolve(user_override=provided_id)

        # 2. RESOLVE SETTINGS
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
        # Inject trace_id into settings
        settings.setdefault("trace_id", self._trace_id)

        return self._manager.get_handle(uri, as_sink=as_sink, **settings)

    def read(self, uri: str, **settings) -> Any:
        """Convenience: Read entire stream contents as Packets."""
        settings.setdefault("trace_id", self._trace_id)
        return self._manager.read(uri, **settings)

    def write(self, uri: str, data: Any, **settings) -> None:
        """Convenience: Write data to a stream via a Packet."""
        settings.setdefault("trace_id", self._trace_id)
        self._manager.write(uri, data, **settings)

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

    def pipeline(self, uri:str, **settings) -> Any:
        """
        Entrypoint for Pipeline Sub-system
        """
        #settings.setdefault("trace_id", self._trace_id)
        pass