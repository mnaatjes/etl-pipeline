# src/app/use_cases/manager.py

from typing import Any, Dict, Optional
from src.app.registry.streams import StreamRegistry
from src.app.ports.output.datastream import DataStream
from src.app.domain.models.app_config import AppConfig
from src.app.domain.services.settings_resolver import SettingsResolver

class StreamManager:
    def __init__(self, registry:StreamRegistry, app_config:AppConfig, resolver:SettingsResolver) -> None:
        """
        - SRP: Orchestrates lifecycle of a stream
        - Resolves the 'Blueprint'
        - Does NOT do:
            > read/write
            > know about protocols
            > validate properties of Contracts

        :param registry: The catalog of known protocols and their blueprints.
        :param app_config: Tier 1 (Global) settings baseline.
        :param resolver: The 'Waterfall Engine' that calculates the final settings bag.
        """
        self._registry = registry
        self._app_config = app_config
        self._resolver = resolver

    def get_stream(
            self,
            uri:str,
            as_sink:bool=False,
            **overrides
    ) -> DataStream:
        """
        Main entry point to obtain a validated, ready-to-use DataStream.
        
        :param uri: The logical URI (e.g., 's3://bucket/file.json').
        :param as_sink: Whether the stream is for writing (True) or reading (False).
        :param overrides: Tier 3 (Local) settings provided at the call-site.
        """
        # 1. IDENTIFY: Determine the protocol
        protocol = uri.split("://")[0]

        # 2. DISCOVER: Get the 'Blueprint' (Adapter<DataStream>Cls, StreamPolicy)
        blueprint = self._registry.get_registration(protocol)

        # 3. RESOLVE: Use Policy, resolve logical_uri to technical_uri
        # e.g. 'mock://data' --> '/opt/data/file_name.csv'
        # Set final_uri and check for policy to resolve if present
        final_uri = uri
        if blueprint.policy:
            # Policy present --> resolve()
            final_uri = blueprint.policy.resolve(uri)
            # Validate prior to stream instantiation
            blueprint.policy.validate_access(final_uri)
        
        # 4. CALCULATE: Run SettingsResolver Waterfall
        settings = self._resolver.resolve(self._app_config, overrides)

        # 5. INSTANTIATE: Return DataStream instance
        return blueprint.adapter_cls(
            uri=final_uri,
            as_sink=as_sink,
            policy=blueprint.policy,
            **settings
        )
