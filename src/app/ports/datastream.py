# src/app/ports/datastream.py

from abc import ABC, abstractmethod

class DataStream(ABC):
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

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()