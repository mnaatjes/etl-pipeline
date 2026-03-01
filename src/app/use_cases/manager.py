# src/app/use_cases/manager.py

from typing import Any, Dict, Optional
from src.app.registry.streams import StreamRegistry
from src.app.ports.output.datastream import DataStream

class StreamManager:
    def __init__(self, registry:StreamRegistry) -> None:
        """
        - SRP: Orchestrates lifecycle of a stream
        - Resolves the 'Blueprint'
        - Does NOT do:
            > read/write
            > know about protocols
            > validate properties of Contracts

        :param registry: The catalog of known protocols (http, s3, etc.)
        :param global_config: Tier 1 settings (from AppConfig/YAML)
        """