# src/app/ports/output/datastream.py
from dataclasses import fields
from abc import ABC, abstractmethod
from typing import Type, Iterator, Optional
from src.app.ports.output.stream_policy import StreamPolicy
from src.app.ports.output.stream_contract import StreamContract
from src.app.domain.models.envelope import Envelope

class DataStream(ABC):
    def __init__(
            self, 
            uri:str,
            as_sink:Optional[bool] = False,
            policy:Optional[StreamPolicy] = None,
            **settings
    ) -> None:
        """
        The standard constructor for all DataStreams.
        :param as_sink: Whether the stream is intended for writing (True) or reading (False).
        """
        # Assign Common Properties
        self._uri = uri
        self._policy = policy
        self._as_sink = as_sink
        self._settings = settings

        # 1. Filter: Prevent 'Unexpected Keyword' crashes from Global Config
        valid_fields = {f.name for f in fields(self.settings_contract)}
        filtered = {k: v for k, v in settings.items() if k in valid_fields}

        # 2. Hydrate: Triggers __init__ AND the base __post_init__ type-check
        try:
            self.contract = self.settings_contract(**filtered)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Stream Initialization Failed: {e}")

    # --- ABSTRACT PROPERTIES ---

    @property
    @abstractmethod
    def settings_contract(self) -> Type[StreamContract]:
        """Mandatory Hook for Adapters."""
        pass


    # --- CONCRETE PROPERTIES ---

    @property
    def chunk_size(self) -> int:
        """Example: A platform-wide setting accessed via the bag."""
        return self._settings.get("chunk_size", 1024)

    # --- ABSTRACT METHODS ---

    @abstractmethod
    def open(self) -> None: pass
    
    @abstractmethod
    def read(self) -> Iterator[Envelope]:
        """Implementation must yield an Envelope object(s)"""
        yield from []

    def write(self, envelope:Envelope) -> None:
        """
        Default implementation. 
        We don't use @abstractmethod so that Read-Only adapters 
        don't HAVE to implement it.
        """
        raise NotImplementedError(
            f"The adapter {self.__class__.__name__} does not support writing."
        )
    
    @abstractmethod
    def close(self): pass
    
    @abstractmethod
    def exists(self) -> bool:
        """
        Check physical/external availability.
        Returns True if the resource can be reached/accessed.
        """
        pass

    # --- CONCRETE METHODS ---

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()