# src/app/domain/models/streams/stream_handle.py
from typing import Iterator, Any, List, TYPE_CHECKING, Optional
from src.app.domain.models.streams.stream_capacity import StreamCapacity
from src.app.domain.models.streams.stream_context import StreamContext
from src.app.domain.models.packet.base import Packet
from src.app.domain.models.middleware.catalog import MiddlewareCatalog
from src.app.domain.models.middleware.engine import MiddlewareEngine

if TYPE_CHECKING:
    from src.app.ports.output.datastream import DataStream
    from src.app.ports.output.middleware_processor import MiddlewareProcessor

class StreamHandle:
    """
    The Orchestrated Dashboard for a Slalom DataStream.
    
    This class acts as the 'Composition Root' for a single stream's life.
    It manages the localized middleware chain, handles identity context (Passport),
    and orchestrates the transformation engine between the user and the adapter.
    """
    
    def __init__(
        self, 
        adapter: 'DataStream', 
        capacity: StreamCapacity, 
        context: StreamContext, 
        processors: Optional[List['MiddlewareProcessor']] = None
    ) -> None:
        """
        Initializes the Handle with a physical adapter and optional transformations.
        
        Args:
            adapter (DataStream): The physical I/O adapter (e.g., PosixFileStream).
            capacity (StreamCapacity): The technical capabilities of the adapter.
            context (StreamContext): The session/traceability context for the stream.
            processors (Optional[List[MiddlewareProcessor]]): An initial set of 
                transformations to apply. Defaults to None.
        """
        # Define Props
        self._adapter = adapter   # The Physical Worker
        self.capacity = capacity  # The Capability Inspector
        self.context  = context   # The Traceability Passport
        self.uri      = adapter.uri

        # Localized Middleware Subsystem
        self._catalog = MiddlewareCatalog(processors)
        self._engine  = MiddlewareEngine(self._catalog)

    # --- PROPERTIES ---

    @property
    def is_open(self) -> bool:
        """Proxies the open state of the underlying physical adapter."""
        return self._adapter.is_open
    
    @property
    def middleware(self) -> List['MiddlewareProcessor']:
        """
        Dashboard: Retrieves all active transformation objects in the local chain.
        
        Returns:
            List[MiddlewareProcessor]: The current list of processors.
        """
        return self._catalog.get_all()

    # --- ACTION METHODS ---

    def add_processor(self, processor: 'MiddlewareProcessor') -> None:
        """
        Decorates the stream with a new transformation processor.
        
        Args:
            processor (MiddlewareProcessor): The processor instance to add.
            
        Example:
            >>> handle.add_processor(GzipDecompressor())
        """
        self._catalog.add(processor)

    def read(self) -> Iterator[Packet]:
        """
        Orchestrated Read: Pulls raw packets and flows them Downstream.
        
        The data follows the path: Adapter -> Middleware -> User.
        
        Returns:
            Iterator[Packet]: A generator of fully transformed packets.
            
        Raises:
            IOError: If the stream is not open.
        """
        if not self.is_open:
            raise IOError(f"Attempted to read from a closed stream: {self.uri}")
        
        # Handoff to the engine's Interceptor for functional chaining
        return self._engine.intercept(
            self._adapter.read()
        )

    def write(self, payload: Any) -> None:
        """
        Orchestrated Write: Takes raw payload and flows it Downstream.
        
        The data follows the path: User -> Middleware -> Adapter.
        
        Args:
            payload (Any): The data to be processed and written.
            
        Raises:
            PermissionError: If the stream is read-only.
        """
        if not self.capacity.is_writable:
            raise PermissionError(f"Stream is read-only: {self.uri}")
        
        # Promotion: Wrap raw payload in a Packet passport
        packet = Packet(payload=payload, context=self.context)

        # Transformation: Drive packet downstream through the local engine
        for processed in self._engine.process(packet):
            # Persistence: Deliver the transformed packet to the adapter
            self._adapter.write(processed)

    # --- CONTEXT MANAGER ---

    def __enter__(self) -> 'StreamHandle':
        """
        Initializes the physical connection and all middleware resources.
        
        Returns:
            StreamHandle: The ready-to-use handle instance.
        """
        # 1. Open Physical Resource
        self._adapter.__enter__()
        # 2. Open Middleware Resources
        self._engine.open_all()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Gracefully drains buffers and releases all system resources.
        """
        # 1. Residual Flow: Flush writing buffers before closing the sink
        if self.capacity.is_writable and self.is_open:
            for packet in self._engine.flush():
                self._adapter.write(packet)

        # 2. Teardown Middleware
        self._engine.close_all()
        
        # 3. Teardown Physical Adapter
        self._adapter.__exit__(exc_type, exc_val, exc_tb)

    # --- UTILITY METHODS ---

    def list_processors(self) -> List[str]:
        """
        Returns the class names of all active processors in the chain.
        
        Returns:
            List[str]: A list of processor names (e.g., ['GzipDecompressor']).
        """
        return [p.__class__.__name__ for p in self.middleware]
