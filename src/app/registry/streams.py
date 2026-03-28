# src/app/registry/streams.py
from dataclasses import dataclass
from src.app.domain.models.streams.adapter_blueprint import AdapterBlueprint
from typing import Dict

class StreamRegistry:
    def __init__(self):
        self._protocols: dict[str, AdapterBlueprint] = {}

    def register(self, blueprint: AdapterBlueprint):
        """Stores the blueprint with its associated realm."""
        self._protocols[blueprint.protocol] = blueprint

    def get_registration(self, protocol: str) -> AdapterBlueprint:
        """Retrieves the blueprint for the Manager."""
        if protocol not in self._protocols:
            raise ValueError(f"No adapter registered for protocol: {protocol}")
        return self._protocols[protocol]
    
    def is_supported(self, protocol:str) -> bool:
        """Helper to check if a protocol has a registered adapter"""
        return protocol in self._protocols

    def get_all(self) -> Dict[str, AdapterBlueprint]:
        """Returns the contents of the registry"""
        return self._protocols