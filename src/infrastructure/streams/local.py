# src/infrastructure/streams/local.py
from ...app import DataStream
from pathlib import Path

class LocalFileStream(DataStream):
    def __init__(self, uri:str, mode:str="rb"): 
        self.path   = uri.replace("file://", "") # File does not like protocol 'file://'; strip protocol
        self._file  = None # Private Instance Attribute that holds the File Object, i.e. 'handle' or 'stream'
        self.mode   = mode # Defaults to Read-Binary

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
            
        self._file = open(self.path, self.mode)

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
        while chunk := self._file.read(4096): yield chunk

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

        self._file.write(chunk)

    def close(self): 
        # Only attempt to close if handle exists
        if self._file is not None:
            self._file.close()
            # Reset to None for safety
            self._file = None