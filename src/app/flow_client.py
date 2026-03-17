# src/app/stream_client.py

from typing import Optional, Dict, Any
from src.app.container import ServiceContainer
from src.app.domain.services.traceability_provider import TraceabilityProvider

class Flow:

    def __init__(
            self,
            config: Optional[Dict[str, Any]] = None,
            trace_id: Optional[str] = None,
            container: Optional[ServiceContainer] = None
    ) -> None:
        # 1. TRACE ID
        # - Initialize config-bag dict
        # - Check for trace_id being passed as argument
        # - Use TraceProvider service to resolve --> Produces Trace_id
        config_bag      = config or {}
        provided_id     = trace_id or config_bag.get("trace_id")
        self._trace_id  = TraceabilityProvider.resolve(user_override=provided_id)

        # 2. CONTAINER
        # - IoC: Check for ServiceContainer as argument
        # - Else, create ServiceContainer instance from bootstrap
        if container:
            self._container = container
        else:
            from src.app.bootstrap import Bootstrap
            self._container = Bootstrap.initialize(overrides=config_bag)

        # 3. ORCHESTRATORS
        # - Resolve orchestrators as class properties
        self._manager  = self._container.stream_manager
        self._pipeline = self._container.pipeline_runner

    # --- STREAM METHODS: Basic Stream Operations ---

    def read(self, uri:str, **settings) -> Any:
        """Stream Manager reads entire stream contents"""
        
        