# src/app/ports/datastream.py

from abc import ABC, abstractmethod
from typing import Any

from .policy import BasePolicy

class DataStream(ABC):
    def __init__(self, resource_configuration:Any, chunk_size:int, as_sink:bool=False, policy:BasePolicy|None=None) -> None:
        """
        The standard constructor for all DataStreams.
        :param resource_config: The resolved path, URL, or DSN.
        :param as_sink: Whether the stream is intended for writing (True) or reading (False).
        """
        # Assign Dependencies
        self.resource_conf = resource_configuration
        self._chunk_size = chunk_size
        self.as_sink=as_sink
        self._policy = policy

    @abstractmethod
    def open(self): pass
    
    @abstractmethod
    def read(self): yield from []

    def write(self, chunk: bytes):
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

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()