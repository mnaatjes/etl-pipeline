# src/app/domain/models/middleware/catalog.py
from typing import Optional, List, Iterator
from src.app.ports.output.middleware_processor import MiddlewareProcessor

class MiddlewareCatalog:
    """
    The Localized Registry for a StreamHandle's transformations.
    
    This class acts as a 'Librarian' for a specific stream's middleware chain.
    It encapsulates the storage and discovery of MiddlewareProcessors,
    ensuring that transformations are isolated to the specific stream instance.
    """
    
    def __init__(self, processors: Optional[List[MiddlewareProcessor]] = None) -> None:
        """
        Initializes the Catalog with an optional starting set of processors.
        
        Args:
            processors (Optional[List[MiddlewareProcessor]]): Initial list of 
                transformations to apply to the stream. Defaults to None.
        """
        # Localized Storage
        self._processors: List[MiddlewareProcessor] = processors or []

    def add(self, processor: MiddlewareProcessor) -> None:
        """
        Appends a new transformation processor to the local chain.
        
        Args:
            processor (MiddlewareProcessor): The processor instance to add 
                to the end of the execution pipeline.
                
        Example:
            >>> catalog.add(ChecksumProcessor(algorithm="sha256"))
        """
        self._processors.append(processor)

    def get_all(self) -> List[MiddlewareProcessor]:
        """
        Retrieves a read-only snapshot of the active transformation chain.
        
        Returns:
            List[MiddlewareProcessor]: A list of all registered processors.
            
        Example:
            >>> [p.__class__.__name__ for p in catalog.get_all()]
            ['GzipProcessor', 'JsonProcessor']
        """
        return list(self._processors)
    
    def __iter__(self) -> Iterator[MiddlewareProcessor]:
        """
        Provides iterative access to the registered processors.
        
        Returns:
            Iterator[MiddlewareProcessor]: An iterator over the internal 
                processor list.
                
        Example:
            >>> for processor in catalog:
            ...     print(processor)
        """
        return iter(self._processors)

    def __len__(self) -> int:
        """
        Returns the number of processors currently in the catalog.
        
        Returns:
            int: The count of registered MiddlewareProcessors.
            
        Example:
            >>> if len(catalog) > 0:
            ...     print("Transformations are active")
        """
        return len(self._processors)

    def __getitem__(self, index: int) -> MiddlewareProcessor:
        """
        Allows indexed access to specific processors in the chain.
        
        Args:
            index (int): The 0-based index of the processor to retrieve.
            
        Returns:
            MiddlewareProcessor: The processor at the specified index.
            
        Raises:
            IndexError: If the index is out of bounds.
        """
        return self._processors[index]
