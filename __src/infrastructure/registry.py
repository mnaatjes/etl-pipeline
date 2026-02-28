# src/infrastructure/registry.py

# Libraries
from dataclasses import dataclass
from typing import Type, Optional
# Dependencies
from src.app import DataStream, BasePolicy
from src.infrastructure import LocalFileStream, RemoteHttpStream

from dataclasses import dataclass
from typing import Dict, Type, Optional

# --- Ports (Abstracts) ---
from src.app.ports.datastream import DataStream
from src.app.ports.policy import BasePolicy

# --- Adapters (Concrete) ---
from src.infrastructure.streams.local.adapter import LocalFileStream
from src.infrastructure.streams.http.adapter import RemoteHttpStream

@dataclass(frozen=True)
class ProtocolRegistration:
    """
    The 'Blueprint' for a registered protocol.
    Wraps the Adapter class and its optional Policy into a single type.
    """
    adapter_cls: Type[DataStream]
    policy: Optional[BasePolicy] = None


class StreamRegistry:
    """
    The Infrastructure Catalog.
    Responsibility: Mapping URI protocols (e.g., 'http') to physical Adapters.
    """

    def __init__(self):
        # 1. Initialize the internal catalog using the Registration type
        self._protocols: Dict[str, ProtocolRegistration] = {}

        # 2. Self-Register the "Native" Adapters provided by the library
        self.register("file", LocalFileStream)
        self.register("http", RemoteHttpStream)
        self.register("https", RemoteHttpStream)

    def register(
        self, 
        protocol: str, 
        adapter_cls: Type[DataStream], 
        policy: Optional[BasePolicy] = None
    ) -> None:
        """
        The Extension Hook.
        Allows adding custom protocols (e.g., 's3', 'db') at runtime.
        """
        if not issubclass(adapter_cls, DataStream):
            raise TypeError(
                f"Adapter for protocol '{protocol}' must inherit from DataStream. "
                f"Received: {adapter_cls.__name__}"
            )

        # Store the registration object
        self._protocols[protocol] = ProtocolRegistration(
            adapter_cls=adapter_cls,
            policy=policy
        )

    def get_stream(self, uri: str, as_sink: bool = False, **settings) -> DataStream:
        """
        The Factory Method.
        Resolves the protocol from the URI and returns an instantiated adapter.
        """
        # Extract protocol (e.g., 'http://...' -> 'http')
        protocol = uri.split("://")[0]

        registration = self._protocols.get(protocol)

        if not registration:
            available = ", ".join(self._protocols.keys())
            raise ValueError(
                f"Unsupported protocol: '{protocol}'. Available protocols: {available}"
            )

        # Instantiate the adapter class with the merged settings
        # The 'settings' here are the final Tier 1-3 merged Waterfall results
        return registration.adapter_cls(uri, as_sink=as_sink, **settings)