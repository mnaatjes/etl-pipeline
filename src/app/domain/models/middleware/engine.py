# src/app/domain/models/middleware/engine.py
from typing import Iterator
from src.app.domain.models.middleware.catalog import MiddlewareCatalog
from src.app.domain.models.packet import Packet

class MiddlewareEngine:
    """
    The Execution Engine for the Middleware Subsystem.
    
    SRP: Handles the recursive, depth-first transformation of Packets 
    through a sequence of MiddlewareProcessors. It is 'Driven' by a 
    MiddlewareCatalog and ensures both active and residual (flushed) 
    data is correctly processed.
    """

    def __init__(self, catalog: MiddlewareCatalog) -> None:
        """
        Initializes the Engine with a reference to a Localized Catalog.
        
        Args:
            catalog (MiddlewareCatalog): The librarian holding the 
                active processor chain for this execution context.
        """
        # Dependency
        self._catalog = catalog
    

    def process(self, packet: Packet) -> Iterator[Packet]:
        """
        Entry Point: Pipes a raw packet through the transformation chain.
        
        Args:
            packet (Packet): The raw input packet from the source stream.
            
        Yields:
            Iterator[Packet]: The final, fully transformed packets.
            
        Example:
            >>> for processed in engine.process(raw_packet):
            ...     print(processed.payload)
        """
        yield from self._apply_chain(packet, 0)

    def intercept(self, stream: Iterator[Packet]) -> Iterator[Packet]:
        """
        The Pipeline Interceptor: Wraps a raw packet source with the 
        transformation chain.
        
        This is the core 'Functional Chaining' mechanism that allows the 
        StreamHandle to remain decoupled from the transformation logic.
        
        Args:
            stream (Iterator[Packet]): A raw source of packets (usually 
                from a DataStream adapter).
                
        Yields:
            Iterator[Packet]: A transformed stream of packets, including 
                any residual data flushed from the chain.
                
        Example:
            >>> transformed_stream = engine.intercept(adapter.read())
            >>> for packet in transformed_stream:
            ...     print(packet.payload)
        """
        # 1. Active Flow: Drive the source through the engine's processors
        for packet in stream:
            # Each raw packet could produce 0, 1, or many processed packets
            yield from self.process(packet)
        
        # 2. Residual Flow: Ensure all buffers are drained once the source ends
        yield from self.flush()

    def _apply_chain(self, packet: Packet, index: int) -> Iterator[Packet]:
        """
        Recursive Motor: Depth-first transformation of packets.
        
        Args:
            packet (Packet): The packet to be processed at the current stage.
            index (int): The index of the current processor in the catalog.
            
        Yields:
            Iterator[Packet]: Packets that have survived the remainder of the chain.
        """
        # Check if processors remain
        if index >= len(self._catalog):
            yield packet
            return
        
        # Grab processor
        processor = self._catalog[index]
        for processed in processor.process(packet):
            yield from self._apply_chain(processed, index + 1)
    
    def flush(self) -> Iterator[Packet]:
        """
        Exit Point: Drains all internal buffers from the processor chain.
        
        This should be called once after the source stream is exhausted 
        to ensure no data is left behind in stateful processors.
        
        Yields:
            Iterator[Packet]: Any residual packets trapped in buffers.
            
        Example:
            >>> for residual in engine.flush():
            ...     storage.append(residual)
        """
        yield from self._flush_recursive(0)

    def _flush_recursive(self, index: int) -> Iterator[Packet]:
        """
        Recursive Draining: Orderly flush from start to end of chain.
        
        Args:
            index (int): The index of the processor to flush.
            
        Yields:
            Iterator[Packet]: Flushed packets passed through the rest of the chain.
        """
        # End of chain
        if index >= len(self._catalog):
            return
        
        processor = self._catalog[index]
        for flushed in processor.flush():
            yield from self._pipe_remaining(flushed, index + 1)

        # Yield from next processor and repeat flush
        yield from self._flush_recursive(index + 1)

    def _pipe_remaining(self, packet: Packet, start_index: int) -> Iterator[Packet]:
        """
        Utility: Pipes a single packet through the remainder of the chain.
        
        Used primarily by the flushing mechanism to handle late-arriving packets.
        
        Args:
            packet (Packet): The packet yielded during a flush operation.
            start_index (int): The point in the chain to begin processing.
            
        Yields:
            Iterator[Packet]: The result of the remaining transformations.
        """
        yield from self._apply_chain(packet, start_index)
    
    def open_all(self) -> None:
        """
        Initializes all processors in the catalog.
        
        Should be called before any processing begins to ensure external 
        resources are ready.
        
        Example:
            >>> engine.open_all()
        """
        for p in self._catalog:
            p.open()
    
    def close_all(self) -> None:
        """
        Closes all processors in the catalog, releasing resources.
        
        Should be called after all processing and flushing is complete.
        
        Example:
            >>> engine.close_all()
        """
        for p in self._catalog:
            p.close()
