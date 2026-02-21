# src/infrastructure/streams/local.py
from ...app import DataStream

class LocalFileStream(DataStream):
    def __init__(self, path): 
        self.path   = path
        self._file  = None # Private Instance Attribute that holds the File Object, i.e. 'handle' or 'stream'

    def open(self):
        """
        Handshake
        - Checks if exists
        - Checks permissions
        - Places pointer at beginning of the file
        
        Virtually zero memory Impact and allows OS to reserve the resource
        """
        self._file = open(self.path, 'rb')

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
        if not self._file:
            raise IOError("Stream not open for writing")
        
        self._file.write(chunk)


    def close(self): 
        # Only attempt to close if handle exists
        if self._file is not None:
            self._file.close()
            # Reset to None for safety
            self._file = None