# src/infrastructure/adapters/http/adapter.py
import httpx
from typing import Type, ContextManager, Optional, Iterator
from src.app.ports.output.stream_policy import StreamPolicy
from src.app.ports.output.datastream import DataStream
from src.app.domain.models.resource_identity import RemoteURL, StreamLocation, PhysicalURI
from src.app.domain.models.streams import StreamCapacity, StreamContext
from src.app.domain.models.packet import Packet, FlowSignal, PayloadSubject, Completeness
from src.infrastructure.adapters.http.contract import HttpContract, HttpReadMode

class HttpStream(DataStream[HttpContract]):
    """
    Modern HTTP/HTTPS Adapter using httpx.
    Specialized for high-performance streaming and strict type safety.
    """
    def __init__(
            self, 
            uri: RemoteURL,
            context: StreamContext,
            as_sink: bool|None = False,
            policy: StreamPolicy|None = None, 
            **settings
    ) -> None:
        """
        Initializes the HTTP Transport.
        :param context: The StreamContext (Passport) inherited from DataStream.
        """
        if as_sink:
            raise NotImplementedError("HTTP Sink not supported.")
        
        # DataStream parameters
        super().__init__(uri, context, as_sink, policy, **settings)

        # 0. RUNTIME INTEGRITY GUARD
        if not isinstance(uri, str) or "://" not in uri:
            raise TypeError(
                f"HttpStream integrity violation. Expected RemoteURL (string), "
                f"but received {type(uri)}."
            )
        # Cast as str from RemoteURL
        self._url: str = str(uri)

        # 1. THE CONNECTION POOL (The Engine)
        self._client: Optional[httpx.Client] = None 

        # 2. THE TRANSPORT VALVE (The Network Pipe)
        # Named uniquely to avoid collision with self._context (The Passport)
        self._transport_valve: Optional[ContextManager] = None

        # 3. THE TRANSPORT RESPONSE (The Data Payload)
        self._response: Optional[httpx.Response] = None

    # --- PROPERTIES ---

    @property
    def capacity(self) -> StreamCapacity:
        """
        HTTP Streams are 'Network' resources:
        They are typically read-only and sequential (non-seekable).
        """
        return StreamCapacity(
            can_seek=False,
            is_readable=True,
            is_writable=False,
            supports_append=False,
            is_network=True
        )

    @property
    def _settings_contract(self) -> Type[HttpContract]:
        """The 'Sieve' that filters global AppConfig for HTTP-only needs."""
        return HttpContract
    
    def open(self) -> None:
        """Init the connection pool"""
        if self._client is None:
            self._client = httpx.Client(
                verify=self._settings.verify_ssl,
                timeout=self._settings.timeout,
                headers=self._settings.headers
            )
    
    @classmethod
    def exists(cls, location: StreamLocation) -> bool:
        """Atomic Existence Check via HEAD request."""
        if not isinstance(location, PhysicalURI):
            return False

        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.head(str(location))
                return response.is_success
        except (httpx.RequestError, httpx.HTTPStatusError):
            return False

    def read(self) -> Iterator[Packet]:
        """
        Enters the transport valve and yields traceable Packets.
        """
        if self._client is None:
            self.open()

        if not self._client:
            raise RuntimeError(f"Transport client failed to initialize.")
        
        # Prepare Request
        request_kwargs = {
            "method": self._settings.method,
            "url": self._url,
            "params": self._settings.params
        }

        payload_methods = {"POST", "PUT", "PATCH", "DELETE"}
        if self._settings.method in payload_methods and self._settings.request_body:
            body = self._settings.request_body
            if isinstance(body, (dict,list)):
                request_kwargs["json"] = body
            else:                    
                request_kwargs["content"] = self._settings.request_body

        # Open the Valve
        self._transport_valve = self._client.stream(**request_kwargs)
        self._response = self._transport_valve.__enter__()
        self._response.raise_for_status()

        # Strategy Dispatch
        strategy_map = {
            HttpReadMode.BYTES: self._read_chunks,
            HttpReadMode.LINES: self._read_lines,
            HttpReadMode.TEXT:  self._read_text,
            HttpReadMode.RAW:   self._read_raw,
        }

        strategy = strategy_map.get(
            self._settings.read_mode, 
            self._read_chunks 
        )

        yield from strategy()

    def close(self) -> None:
        """Properly unwinds the network stack."""
        # 1. Close the Valve
        if self._transport_valve:
            try:
                self._transport_valve.__exit__(None, None, None)
            finally:
                self._transport_valve = None
                self._response = None

        # 2. Close the Engine
        if self._client:
            try:
                self._client.close()
            finally:
                self._client = None
    
    # --- INTERNAL STRATEGY METHODS ---

    def _read_chunks(self) -> Iterator[Packet]:
        """Iterates over raw binary chunks."""
        if not self._response:
            return

        for chunk in self._response.iter_bytes(chunk_size=self.chunk_size):
            if chunk:
                yield Packet(
                    payload=chunk,
                    context=self._context, # Stamped with Passport
                    subject=PayloadSubject.BYTES,
                    signal=FlowSignal.STREAM_DATA,
                    completeness=Completeness.PARTIAL,
                    metadata={"mode": "bytes", "uri": self._url}
                )

    def _read_lines(self) -> Iterator[Packet]:
        """Iterates over UTF-8 encoded lines."""
        if not self._response:
            return

        for line in self._response.iter_lines():
            if line:
                yield Packet(
                    payload=line.encode("utf-8"),
                    context=self._context,
                    subject=PayloadSubject.BYTES,
                    signal=FlowSignal.STREAM_DATA,
                    completeness=Completeness.COMPLETE,
                    metadata={"mode": "lines"}
                )

    def _read_text(self) -> Iterator[Packet]:
        """Iterates over decoded text chunks."""
        if not self._response:
            return

        for text_chunk in self._response.iter_text(chunk_size=self.chunk_size):
            if text_chunk:
                yield Packet(
                    payload=text_chunk.encode("utf-8"),
                    context=self._context,
                    subject=PayloadSubject.BYTES,
                    signal=FlowSignal.STREAM_DATA,
                    completeness=Completeness.PARTIAL,
                    metadata={"mode": "text"}
                )

    def _read_raw(self) -> Iterator[Packet]:
        """Direct socket pull (uncompressed)."""
        if not self._response:
            return

        for raw_chunk in self._response.iter_raw():
            if raw_chunk:
                yield Packet(
                    payload=raw_chunk,
                    context=self._context,
                    subject=PayloadSubject.BYTES,
                    signal=FlowSignal.STREAM_DATA,
                    completeness=Completeness.PARTIAL,
                    metadata={"mode": "raw", "compressed": True}
                )
