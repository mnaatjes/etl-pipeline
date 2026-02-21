# src/infrastructure/streams/http.py
import httpx
from typing import Optional, ContextManager
from ...app import DataStream

import httpx
from typing import Any
from src.app.ports.datastream import DataStream

class RemoteHttpStream(DataStream):
    def __init__(self, url: str, as_sink: bool=False):
        # Ensure not attempting sink before initialization of super()
        if as_sink:
            raise NotImplementedError("HTTP Sink not supported.")
        super().__init__(url, as_sink)
        self.url = url
        self._client:Optional[httpx.Client]=None
        self._response: Optional[httpx.Response]=None   # Actual Responce Object
        self._context: Optional[ContextManager]=None    # Context Manager returned by httpx.stream()

    def exists(self) -> bool:
        """Lightweight HEAD request to verify resource availability."""
        with httpx.Client(follow_redirects=True) as client:
            try:
                # HEAD request doesn't download the body
                res = client.head(self.url, timeout=5.0)
                return res.is_success
            except httpx.RequestError:
                return False

    def open(self):
        """Establish the streaming connection."""
        self._client = httpx.Client(follow_redirects=True)
        # 1. Create the stream context manager
        self._context = self._client.stream("GET", self.url)

        # 2. Enter contect and store response
        self._response = self._context.__enter__()

        # 3. Type Guard for IDE and Runtime Check
        if self._response is None:
            raise RuntimeError(f"httpx failed to initialize the response object for url {self.url}")
        
        # 4. Raise exceptions if any
        self._response.raise_for_status()

    def read(self):
        if not self._response:
            raise RuntimeError("Stream not opened. Use 'with' statement.")
        
        # Standard 4KB chunks for Linux-friendly I/O
        for chunk in self._response.iter_bytes(chunk_size=4096):
            yield chunk

    def close(self):
        # 1. Close Context Manager
        if self._context:
            self._context.__exit__(None, None, None)

        # 2. Close Client (Connection Pool)
        if self._client:
            self._client.close()
        
        # 3. Wipe all references
        self._client = None
        self._context = None
        self._response = None