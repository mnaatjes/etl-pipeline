# src/app/registry/streams.py
from typing import Type, Optional
from dataclasses import dataclass
from src.app.ports.output.datastream import DataStream
from src.app.ports.output.stream_policy import StreamPolicy

@dataclass(frozen=True)
class ProtocolRegistration:
    adapter_cls: Type[DataStream]
    policy: Optional[StreamPolicy] = None

class StreamRegistry:
    def __init__(self):
        self._protocols: dict[str, ProtocolRegistration] = {}

    def register(self, protocol: str, adapter_cls: Type[DataStream], policy: Optional[StreamPolicy] = None):
        """Stores the blueprint. No settings passed here."""
        self._protocols[protocol] = ProtocolRegistration(
            adapter_cls=adapter_cls, 
            policy=policy
        )

    def get_registration(self, protocol: str) -> ProtocolRegistration:
        """Retrieves the blueprint for the Manager."""
        if protocol not in self._protocols:
            raise ValueError(f"No adapter registered for protocol: {protocol}")
        return self._protocols[protocol]