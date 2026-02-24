# src/infrastructure/registry.py

# Libraries
from dataclasses import dataclass
from typing import Type, Optional
# Dependencies
from src.app import DataStream, BasePolicy
from .streams.local import LocalFileStream
from .streams.http import RemoteHttpStream
from .streams.db_table import DbTableStream

@dataclass(frozen=True)
class ProtocolRegistration:
    adapter_cls: Type[DataStream]
    policy: Optional[BasePolicy]

class StreamRegistry:
    def __init__(self, chunk_size:int):
        # Protocols will be mapped at bootstrap phase
        self._protocols: dict[str, ProtocolRegistration] = {}
        self._chunk_size = chunk_size

    def register(self, protocol:str, adapter_cls:Type[DataStream], policy:BasePolicy|None=None) -> None:
        self._protocols[protocol] = ProtocolRegistration(
            adapter_cls=adapter_cls,
            policy=policy,
        )

    def get_stream(self, uri:str, as_sink:bool=False) -> DataStream:
        """
        Method acts as a Factory. 
        - Identifies URI stream
        - Sorts by DataStream implementation
        - Injects appropriate policy
        - Passes boolean 'is_sink'; e.g. determines mode in LocalDataStream
        """
        protocol = uri.split("://")[0]
        # Validate Protocol
        if protocol not in self._protocols:
            raise ValueError(f"The following protocol has not been registed with an adapter: {protocol}")
        
        # Aid IDE by storing ProtocolRegistration in variable
        registration = self._protocols[protocol]
        # Resolve URI if there is a policy; otherwire send uri
        resolved = registration.policy.resolve(uri) if registration.policy else uri
        # Instantiate DataStream and return
        if registration.policy:                
            return registration.adapter_cls(
                resolved,
                chunk_size=self._chunk_size,
                as_sink=as_sink,
                policy=registration.policy
            )
        else:
            return registration.adapter_cls(
                resolved,
                chunk_size=self._chunk_size,
                as_sink=as_sink
            )