# src/infrastructure/streams/local.py
from pathlib import Path
# Use the 'app' gateway
from src.app import DataStream, BasePolicy

class LocalFileStream(DataStream):
    def __init__(self, path:Path, policy:BasePolicy, chunk_size:int, as_sink:bool=False): 
        super().__init__(str(path), chunk_size=chunk_size, as_sink=as_sink)
        self.path   = path # Converted to a path by StreamRegistry
        self._file  = None # Private Instance Attribute that holds the File Object, i.e. 'handle' or 'stream'        
        self.mode   = "wb" if self.as_sink else "rb"
        self._policy = policy

    def open(self):
        """
        Handshake
        - Checks if exists
        - Checks permissions
        - Places pointer at beginning of the file
        
        Virtually zero memory Impact and allows OS to reserve the resource
        """
        # Check if mode correct and path created
        if "w" in self.mode:
            dir = Path(self.path).parent
            if dir and not dir.exists():
                raise NotADirectoryError(f"Directory does NOT Exist at path: {self.path}")
            
        self._file = open(self.path, self.mode, buffering=self._chunk_size)

    def read(self): 
        """
        Heavy Lifting
        - Reads the file in small chunks
        - 'yield' is a data_generator

        """
        # Guard clause: Check if open() was successful
        if self._file is None:
            raise RuntimeError(
                f"Stream for {self.path} must be opened before reading. "
                "Did you forget to use a 'with' statement?"
            )
        # Perform chunking
        while chunk := self._file.read(self._chunk_size): yield chunk

    def write(self, chunk: bytes):
        """
        Implementation of the write capability.
        """
        # Check file is open
        if self._file is None:
            raise IOError("Stream is not open.")
        # Check file has correct mode for write operations
        if "w" not in self.mode and "a" not in self.mode:
            raise IOError(f"Stream opened with mode '{self.mode}' does not support writing.")
        
        # Guard against un-chunked blocks and leaking chunks
        if len(chunk) > self._chunk_size * 2:
            pass # TODO: Warn User

        # Write chunk to file
        self._file.write(chunk)

    def close(self): 
        # Only attempt to close if handle exists
        if self._file is not None:
            self._file.close()
            # Reset to None for safety
            self._file = None

    def exists(self) -> bool:
        """Checks the physical Linux filesystem."""
        return self.path.exists()
    
    def as_source(self):
        """Returns a new instance of this stream configured for reading."""
        from .local import LocalFileStream # Avoid circular import if needed
        return LocalFileStream(
            path=self.path,
            policy=self._policy,
            chunk_size=self._chunk_size,
            as_sink=False
        )