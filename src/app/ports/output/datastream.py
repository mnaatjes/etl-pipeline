# src/app/ports/output/datastream.py
from dataclasses import fields
from abc import ABC, abstractmethod
from typing import Type, Iterator, Optional, TypeVar, Generic, Dict, Any, List
from src.app.ports.output.stream_policy import StreamPolicy
from src.app.ports.output.stream_contract import StreamContract
from src.app.domain.models.streams.stream_context import StreamContext
from src.app.domain.models.streams.stream_capacity import StreamCapacity
from src.app.domain.models.packet import Packet
from src.app.ports.output.middleware_processor import MiddlewareProcessor

from src.app.domain.models.resource_identity import Coordinate

# Create a TypeVar that represents any subclass of StreamContract
T = TypeVar("T", bound=StreamContract)

class DataStream(ABC, Generic[T]):
    def __init__(
            self, 
            uri:Coordinate,
            context:StreamContext,
            as_sink:Optional[bool] = False,
            policy:Optional[StreamPolicy] = None,
            **settings
    ) -> None:
        """
        The standard constructor for all DataStreams.
        :param as_sink: Whether the stream is intended for writing (True) or reading (False).
        """
        # Initialize Open Property
        self.is_open = False

        # Assign Common Properties
        self._uri       = uri
        self._as_sink   = as_sink
        self._context   = context
        self._policy    = policy

        # 1. Filter: Prevent 'Unexpected Keyword' crashes from Global Config
        valid_fields = {f.name for f in fields(self._settings_contract)}
        filtered = {k: v for k, v in settings.items() if k in valid_fields}

        # 2. Hydrate: Triggers __init__ AND the base __post_init__ type-check
        try:
            self._settings: T = self._settings_contract(**filtered)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Stream Initialization Failed: {e}")

        # 3. STANDALONE MIDDLEWARE
        self._processors: List[MiddlewareProcessor] = []

    # --- MIDDLEWARE METHODS ---

    def inject_processors(self, processors: List[MiddlewareProcessor]) -> None:
        """Adds processors to the standalone stream chain."""
        self._processors.extend(processors)

    def _process_chain(self, packet: Packet) -> Iterator[Packet]:
        """
        Recursive pipe-and-filter implementation for the internal chain.
        This allows 'wrap()' to work on individual stream handles.
        """
        def apply_next(p: Packet, index: int) -> Iterator[Packet]:
            if index >= len(self._processors):
                yield p
                return

            processor = self._processors[index]
            for processed in processor.process(p):
                yield from apply_next(processed, index + 1)

        yield from apply_next(packet, 0)

    def _flush_chain(self) -> Iterator[Packet]:
        """
        Triggers flush() on all processors in the chain and pipes results downstream.
        """
        def flush_recursive(index: int) -> Iterator[Packet]:
            if index >= len(self._processors):
                return

            processor = self._processors[index]
            # 1. Flush this processor
            for flushed_packet in processor.flush():
                # 2. Pipe flushed results through the REMAINING chain
                yield from self._pipe_remaining(flushed_packet, index + 1)
            
            # 3. Move to next processor in the chain
            yield from flush_recursive(index + 1)

        yield from flush_recursive(0)

    def _pipe_remaining(self, packet: Packet, start_index: int) -> Iterator[Packet]:
        """Helper to pipe a flushed packet through the rest of the chain."""
        def apply_next(p: Packet, index: int) -> Iterator[Packet]:
            if index >= len(self._processors):
                yield p
                return

            processor = self._processors[index]
            for processed in processor.process(p):
                yield from apply_next(processed, index + 1)

        yield from apply_next(packet, start_index)

    # --- ABSTRACT PROPERTIES ---

    @property
    @abstractmethod
    def capacity(self) -> StreamCapacity:
        """Mandatory: Adapters must declare capabilities"""
        pass

    @property
    @abstractmethod
    def _settings_contract(self) -> Type[T]:
        """Mandatory Hook for Adapters."""
        pass


    # --- CONCRETE PROPERTIES ---

    @property
    def uri(self) -> Coordinate:
        return self._uri

    @property
    def chunk_size(self) -> int:
        """Example: A platform-wide setting accessed via the bag."""
        return getattr(self._settings, "chunk_size", 1024)

    # --- ABSTRACT METHODS ---

    @abstractmethod
    def open(self) -> None: pass
    
    @abstractmethod
    def read(self) -> Iterator[Packet]:
        """Implementation must yield Packet object(s)"""
        yield from []

    def write(self, packet:Packet) -> None:
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
    
    @classmethod
    @abstractmethod
    def exists(cls, location: Coordinate) -> bool:
        """
        PRE-FLIGHT CHECK (Class Method):
        Determines if the resource exists at the given resolved location 
        without instantiating the stream machinery.
        
        Args:
            location (Coordinate): A LocalCoordinate or NetworkCoordinate.
        """
        pass

    @classmethod
    def list(cls, location: Coordinate) -> Iterator[Coordinate]:
        """Discovery: Lists resources at the given location."""
        raise NotImplementedError(f"{cls.__name__} does not support listing.")

    @classmethod
    def info(cls, location: Coordinate) -> Dict[str, Any]:
        """Metadata: Retrieves technical details about a resource."""
        raise NotImplementedError(f"{cls.__name__} does not support metadata retrieval.")

    @classmethod
    def delete(cls, location: Coordinate) -> bool:
        """CRUD: Removes a physical resource."""
        raise NotImplementedError(f"{cls.__name__} does not support deletion.")

    @classmethod
    def move(cls, src: Coordinate, dest: Coordinate) -> bool:
        """CRUD: Relocates a resource."""
        raise NotImplementedError(f"{cls.__name__} does not support move operations.")

    @classmethod
    def copy(cls, src: Coordinate, dest: Coordinate) -> bool:
        """CRUD: Duplicates a resource."""
        raise NotImplementedError(f"{cls.__name__} does not support copy operations.")

    # --- CONCRETE METHODS ---

    def __enter__(self):
        self.open()
        self.is_open = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.is_open = False
        self.close()