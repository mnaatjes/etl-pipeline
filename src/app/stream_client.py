# src/stream_client.py

from typing import Any, Optional, Dict
from src.app.bootstrap import Bootstrap
from src.app.ports.output.datastream import DataStream

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
        # The 'Big Bang': Manager, Registry, and Resolver are wired here.
        self._manager = Bootstrap.initialize(config_overrides=config)

    def get_stream(
        self, 
        uri: str, 
        as_sink: bool = False, 
        **settings
    ) -> DataStream:
        """
        Requests a validated Stream instance from the Orchestrator.
        
        :param uri: The logical URI (e.g., 'file:///tmp/data.csv').
        :param as_sink: True for writing, False for reading.
        :param settings: Tier 3 (Local) overrides for this specific stream.
        """
        return self._manager.get_stream(uri, as_sink=as_sink, **settings)