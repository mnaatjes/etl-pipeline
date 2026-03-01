# src/infrastructure/adapters/http/adapter.py
import httpx
from typing import Type, ContextManager, Optional, Iterator
from app.ports.output.stream_policy import StreamPolicy
from src.app.ports.output.datastream import DataStream
from src.app.domain.models.envelope import Envelope, RegimeType, Completeness
from src.infrastructure.adapters.http.contract import HttpContract, HttpReadMode

class HttpStream(DataStream[HttpContract]):
    """
    Modern HTTP/HTTPS Adapter using httpx.
    Specialized for high-performance streaming and strict type safety.
    Refactored 03/01/2026

    This class utilizes Python Generics (typing.Generic[T]) to 'lock in' a specific 
    StreamContract at the subclass level. 

    Behavior:
        1. Type Placeholder: In the base `DataStream`, `T` acts as a structural 
        placeholder bound to the `StreamContract` base class.
        2. Static Specialization: By declaring `class HttpStream(DataStream[HttpContract])`, 
        the subclass replaces the generic `T` with a concrete `HttpContract`.
        3. IDE Intelligence: This specialization allows static analysis tools (like 
        Pyright/Pylance) to resolve `self._settings` as the specific contract type 
        rather than the abstract base, enabling autocomplete and type safety 
        for domain-specific fields (e.g., 'headers', 'timeout').

    Requirements for Subclasses:
        - Must provide a concrete `StreamContract` in the class inheritance brackets.
        - Must implement the `_settings_contract` property to return the corresponding 
        Contract class for runtime hydration.
        - The provided Contract must be a subclass of `StreamContract`.

    Example:
        >>> class HttpStream(DataStream[HttpContract]):
        ...     @property
        ...     def _settings_contract(self) -> Type[HttpContract]:
        ...         return HttpContract
    """
    def __init__(
            self, uri: str, 
            as_sink: bool|None = False, 
            policy: StreamPolicy|None = None, 
            **settings
    ) -> None:
        """Pass parameters to DataStream Base Class
        - Validates 'as_sink' not valid
        - Settings filtering and hydration
        - Defines self._uri, self._as_sink, self._policy, self._settings
        """
        if as_sink:
            raise NotImplementedError("HTTP Sink not supported.")
        # DataStream parameters
        super().__init__(uri, as_sink, policy, **settings)

        # 1. THE CONNECTION POOL (The Engine)
        # Represents the underlying TCP/HTTP session. 
        # Managed in open() and close(). Stays alive across multiple reads if needed.
        self._client: Optional[httpx.Client] = None 

        # 2. THE STREAM CONTEXT (The Valve / Lifecycle)
        # The ContextManager returned by httpx.stream(). 
        # It controls the "opening" and "closing" of the actual network pipe.
        # We store it so we can manually exit the context in self.close().
        self._context: Optional[ContextManager] = None

        # 3. THE RESPONSE DATA (The Payload)
        # The actual httpx.Response object. 
        # Provides access to headers, status_codes, and the iter_bytes() method.
        self._response: Optional[httpx.Response] = None

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
    
    def exists(self, persist:bool=False) -> bool:
        """
        Verifies resource availability via a HEAD request.
        
        :param persist: If True, initializes the long-lived self._client. 
                        If False (Default), uses a temporary client that 
                        is destroyed immediately to prevent socket leakage.
        """
        # 1. Check for existing self._client
        # - Client already open
        # - No need to close it
        if self._client:
            try:
                # Return is_success bool value
                return self._client.head(
                    self._uri,
                    timeout=self._settings.timeout
                ).is_success
            except httpx.RequestError:
                # Return failure
                return False
        
        # 2. Lazy Managed: Persistent (True)
        if persist:
            self.open()
            if self._client is None:
                raise ValueError(f"Client unable to open() in exists()! self._client == None")
            try:
                # Return is_success bool value
                return self._client.head(
                    self._uri,
                    timeout=self._settings.timeout
                ).is_success
            except httpx.RequestError:
                # Return failure
                return False
        
        # 3. Safe-by-default: Atomic / persist == False
        # - Does NOT assign value to self._client
        # - Opens and Closes atomic httpx.Client
        try:
            with httpx.Client(verify=self._settings.verify_ssl) as temp_client:
                response = temp_client.head(self._uri, timeout=self._settings.timeout)
                return response.is_success
        except httpx.RequestError:
            return False

    def read(self) -> Iterator[Envelope]:
        """
        Enters the stream context and yields data chunks.
        Stores state in self._response for external probing/validation.
        """
        # 1. CLIENT: Open() / Ensure Httpx Client Open and ready
        # Ensure httpx Client exists
        if self._client is None:
            self.open()

        # Defense check for self._client
        if not self._client:
            raise RuntimeError(f"Transport client - self._client - FAILED to initialize in read()")
        
        # 2. REQUEST: Prepare Arguments
        # Dynamic Request Config
        # - Ensure method, url, params correct
        request_kwargs = {
            "method": self._settings.method,
            "url": self._uri,
            "params": self._settings.params
        }

        # Enforce ability to set body for only POST, PUT, DELETE, PATCH
        payload_methods = {"POST", "PUT", "PATCH", "DELETE"}
        
        # Append Content based on Http Method
        if self._settings.method in payload_methods and self._settings.request_body:
            # Inject Intruction set / request body
            request_kwargs["content"] = self._settings.request_body

        
        # 3. ENTER-STREAM: Use http method and append request properties
        self._context = self._client.stream(**request_kwargs)
        self._response = self._context.__enter__()

        # 4. RESPONSE
        # - Enable TypeGuard for IDE runtime check
        # - Raise Exceptions if any

        self._response.raise_for_status()

        # 5. STRATEGY: Route Read() method
        # - Mapping dict[read_mode:self._read_method]
        strategy_map = {
            HttpReadMode.BYTES: self._read_chunks,
            HttpReadMode.LINES: self._read_lines,
            HttpReadMode.TEXT:  self._read_text,
            HttpReadMode.RAW:   self._read_raw,
        }

        strategy = strategy_map.get(
            self._settings.read_mode,   # Get method from read_mode
            self._read_chunks   # Default: Read Bytes
        )

        # 6. EXECUTE: Yield Envelopes from strategy execution
        yield from strategy()

    def close(self) -> None:
        """
        Properly unwinds the network stack.
        Ensures all Linux file descriptors and sockets are released.
        """
        # 1. THE STREAM SESSION (The 'Valve')
        # We must exit the context manager to signal to the server
        # that we are done with the stream, allowing it to close the connection.
        if self._context:
            try:
                # __exit__ arguments are (Exception Type, Value, Traceback)
                # Passing (None, None, None) signals a clean closure.
                self._context.__exit__(None, None, None)
            except Exception as e:
                # Log or handle unexpected cleanup errors silently 
                # to ensure we still try to close the client.
                pass
            finally:
                self._context = None
                self._response = None

        # 2. THE TRANSPORT ENGINE (The 'Line')
        # Shuts down the connection pool. 
        # This is critical for preventing 'Too many open files' on Linux.
        if self._client:
            try:
                self._client.close()
            finally:
                self._client = None
    
    #-----------------------------------------------------------------------------------#
    # --- READ METHODS ---
    #-----------------------------------------------------------------------------------#

    def _read_chunks(self) -> Iterator[Envelope]:
        """Iterates over raw binary chunks (The Universal Default)."""
        # Type check for safety
        if not self._response:
            return

        for chunk in self._response.iter_bytes(chunk_size=self.chunk_size):
            if chunk:
                yield Envelope(
                    payload=chunk,
                    regime=RegimeType.BYTES,
                    completeness=Completeness.PARTIAL,
                    metadata={"mode": "bytes", "uri": self._uri}
                )

    def _read_lines(self) -> Iterator[Envelope]:
        """Iterates over UTF-8 encoded lines (Ideal for CSV/JSONL)."""
        if not self._response:
            return

        for line in self._response.iter_lines():
            # httpx.iter_lines() yields 'str'; we cast to 'bytes' for predictability
            if line:
                yield Envelope(
                    payload=line.encode("utf-8"),
                    regime=RegimeType.BYTES,
                    completeness=Completeness.COMPLETE, # A line is a finished record
                    metadata={"mode": "lines"}
                )

    def _read_text(self) -> Iterator[Envelope]:
        """Iterates over decoded text chunks (Ideal for large string blobs)."""
        if not self._response:
            return

        for text_chunk in self._response.iter_text(chunk_size=self.chunk_size):
            if text_chunk:
                yield Envelope(
                    payload=text_chunk.encode("utf-8"),
                    regime=RegimeType.BYTES,
                    completeness=Completeness.PARTIAL,
                    metadata={"mode": "text"}
                )

    def _read_raw(self) -> Iterator[Envelope]:
        """Direct socket pull. Bypasses automatic decompression (Gzip/Brotli)."""
        if not self._response:
            return

        # iter_raw() does not accept chunk_size; it yields as data arrives
        for raw_chunk in self._response.iter_raw():
            if raw_chunk:
                yield Envelope(
                    payload=raw_chunk,
                    regime=RegimeType.BYTES,
                    completeness=Completeness.PARTIAL,
                    metadata={"mode": "raw", "compressed": True}
                )