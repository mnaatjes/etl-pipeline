# src/infrastructure/streams/local.py
from pathlib import Path
from typing import Iterator
# Use the 'app' gateway
from src.app import DataStream, BasePolicy
from src.app.ports.envelope import Envelope

class LocalFileStream(DataStream):
    def __init__(self, resource_configuration:Path|str, policy:BasePolicy, chunk_size:int, as_sink:bool=False, use_lines:bool=False):
        # GUARD: Use policy to resolve path
        # Pass safe path to super() as resource_configuration
        resolved_path = policy.resolve(str(resource_configuration))

        super().__init__(str(resolved_path), policy=policy, chunk_size=chunk_size, as_sink=as_sink, use_lines=use_lines)
        self.mode   = "wb" if self._as_sink else "rb"
        self._file  = None # Private Instance Attribute that holds the File Object, i.e. 'handle' or 'stream'
        self._logical_path = resource_configuration

    def open(self) -> None:
        """
        Handshake
        - Checks if exists
        - Checks permissions
        - Places pointer at beginning of the file
        
        Virtually zero memory Impact and allows OS to reserve the resource
        """
        # Check if mode correct and path created
        if "w" in self.mode:
            dir = Path(self._resource_conf).parent
            if dir and not dir.exists():
                raise NotADirectoryError(f"Directory does NOT Exist at path: {self._resource_conf}")
            
        self._file = open(self._resource_conf, self.mode, buffering=self._chunk_size)

    def read(self) -> Iterator[Envelope]: 
        """
        Heavy Lifting
        - Reads the file in small chunks
        - 'yield' is a data_generator

        """
        # Guard clause: Check if open() was successful
        if self._file is None:
            raise RuntimeError(
                f"Stream for {self._resource_conf} must be opened before reading. "
                "Did you forget to use a 'with' statement?"
            )

        if self._use_lines:
            # PATH A: Line-based reading
            for i, line in enumerate(self._file):
                yield Envelope(
                    payload=line, # Already bytes if opened in 'rb'
                    regime="BYTES",
                    metadata={
                        "path": str(self._resource_conf),
                        "chunk_index": i,
                        "bytes_read": len(line)
                    }
                )
        else:
            # PATH B: Traditional block-based reading
            counter = 0
            while chunk := self._file.read(self._chunk_size):
                yield Envelope(
                    payload=chunk,
                    regime="BYTES",
                    metadata={
                        "path": str(self._resource_conf),
                        "chunk_index": counter,
                        "bytes_read": len(chunk)
                    }
                )
                counter += 1

    def write(self, envelope:Envelope):
        """
        Implementation of the write capability.
        """
        # Check file is open
        if self._file is None:
            raise IOError("Stream is not open.")
        # Check file has correct mode for write operations
        if "w" not in self.mode and "a" not in self.mode:
            raise IOError(f"Stream opened with mode '{self.mode}' does not support writing.")
        
        # Unwrap chunk from Envelope
        chunk = envelope.payload
        
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
        return Path(self._resource_conf).exists()
    
    def as_source(self):
        """Returns a new instance of this stream configured for reading."""
        from .local import LocalFileStream # Avoid circular import if needed
        # Check for policy
        if self._policy is None:
            raise ValueError(f"Cannot create a source {self.__class__.__name__} without a Valid Policy!")
        # Return new LocalFileStream as source

        return LocalFileStream(
            resource_configuration=self._resource_conf,
            policy=self._policy,
            chunk_size=self._chunk_size,
            as_sink=False,
            use_lines=self._use_lines
        )