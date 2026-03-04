# src/app/ports/output/middleware_processor.py
from abc import ABC, abstractmethod
from typing import Iterator

from src.app.domain.models.packet import Packet, PayloadType

class MiddlewareProcessor(ABC):
    """
    The Unified Port for all Pipeline Transformations.
    
    Acts as the 'Filter' in a Pipe-and-Filter architecture. Every piece of 
    business logic—whether it's a validator, an aggregator, or a simple 
    regex filter—must implement this interface.
    
    Responsibilities:
    - Resource management (open/close).
    - Lifecycle-aware transformation (process).
    - End-of-stream buffer flushing (flush).
    - Type-safety declarations (input/output subjects).
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The human-readable name of this processor (used for telemetry)."""
        pass

    @property
    @abstractmethod
    def input_subject(self) -> PayloadType:
        """The PayloadType this processor expects to receive as input."""
        pass

    @property
    @abstractmethod
    def output_subject(self) -> PayloadType:
        """The PayloadType this processor guarantees to yield as output."""
        pass

    @abstractmethod
    def process(self, packet: Packet) -> Iterator[Packet]:
        """
        The core transformation logic.
        
        Receives a single Packet and yields zero or more Packet derivatives.
        Use 'packet.spawn(payload=...)' to maintain lineage and context.
        
        :param packet: The incoming unit of work.
        :yield: Transformed or filtered Packets.
        """
        pass

    @abstractmethod
    def flush(self) -> Iterator[Packet]:
        """
        Drains internal buffers upon receiving a STREAM_END signal.
        
        This hook is triggered by the Orchestrator when the source stream 
        is exhausted. Aggregating processors (N:1) should yield their 
        final results here.
        
        :yield: Final buffered Packets.
        """
        yield from []

    def open(self) -> None:
        """
        Initializes external resources (e.g., database connections, file handles).
        
        This method is called once before any packets are processed.
        """
        pass

    def close(self) -> None:
        """
        Cleans up resources and closes active connections.
        
        This method is called once after all packets (including flush) 
        have been processed.
        """
        pass

    # --- CONTEXT MANAGER SUPPORT ---

    def __enter__(self) -> 'MiddlewareProcessor':
        """Allows use of the processor in a 'with' statement."""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Ensures 'close()' is called even if an error occurs."""
        self.close()
