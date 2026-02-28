# /srv/pipeline/src/app/ports/middleware.py
from time import time
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, Iterator, cast
from src.app.ports.envelope import Envelope, RegimeType, Completeness

class BaseMiddleware(ABC):
    """The absolute base for all pipeline processors."""
    def __init__(self, input_regime: RegimeType|str, output_regime: RegimeType|str):
        # Converts to StrEnum value here
        self.input_regime = RegimeType(input_regime) if isinstance(input_regime, str) else input_regime
        self.output_regime = RegimeType(output_regime) if isinstance(output_regime, str) else output_regime

    def __call__(self, envelope: Envelope) -> Iterator[Envelope]:
        """
        Standardized Entry Point
        Middlewares now yields none, a single, or multiple Envelopes
        """
        # Enforce Regime TypeSafety
        # AGNOSTIC CHECK: 
        # If the middleware is set to ANY, it bypasses the Type Safety gate.
        if self.input_regime != RegimeType.ANY and envelope.regime != self.input_regime:
            raise TypeError(
                f"Middleware {self.__class__.__name__} expects {self.input_regime}, "
                f"but received {envelope.regime}"
            )
        
        # Execute Metadata Hook for all child methods
        self.metadata_hook(envelope.metadata)

        for result in self.process(envelope.payload):
            if result is None:
                continue
            
            # MIRRORING LOGIC:
            # If output_regime is ANY, we describe the new envelope 
            # using the incoming envelope's label.
            final_regime = (
                envelope.regime 
                if self.output_regime == RegimeType.ANY 
                else self.output_regime
            )

            yield Envelope(
                payload=result,
                regime=final_regime,
                metadata=envelope.metadata.copy(),
                completeness=envelope.completeness
            )
    
    @abstractmethod
    def process(self, payload: Any) -> Iterator[Any]:
        """The core logic that returns an iterator of results."""
        pass
    
    def metadata_hook(self, metadata: Dict[str, Any]) -> None:
        """
        Optional hook. Subclasses override this to read or add metadata.
        - DO NOT overwrite dict using: metadata={'key':'val'}
        - DO USE: metadata['key'] = 'val'
        """
        pass

class StatefulMiddleware(BaseMiddleware):
    def __init__(self, input_regime: RegimeType, output_regime: RegimeType):
        super().__init__(input_regime, output_regime)
        self._buffer: Any = None # Initialize based on regime (b"" or [])

    @abstractmethod
    def process(self, payload: Any) -> Iterator[Any]:
        pass

class ByteMiddleware(BaseMiddleware):
    """Contract: Input and Output must be bytes."""
    def __init__(self):
            super().__init__(input_regime="BYTES", output_regime="BYTES")

    @abstractmethod
    def process(self, payload: bytes) -> Iterator[bytes]:
            pass

class ObjectMiddleware(BaseMiddleware):
    """
    Contract: Input and Output must be structured objects (dicts/lists).
    Standardizes payload extraction for high-level data manipulation.
    """
    def __init__(self):
        super().__init__(input_regime="OBJECT", output_regime="OBJECT")

    @abstractmethod
    def process(self, payload: dict) -> Iterator[dict]:
        pass

class EncoderMiddleware(BaseMiddleware):
    # REMOVE: the custom __call__ method entirely.
    # BaseMiddleware.__call__ handles the generator flow now.

    def __init__(
            self,
            input_regime: RegimeType,
            output_regime: RegimeType,
            content_type: str = "application/octet-stream",
            encoding: str = "utf-8"
    ) -> None:
        # Use super() to set the regimes in the Base class
        super().__init__(input_regime, output_regime)
        self.content_type = content_type
        self.encoding = encoding

    def metadata_hook(self, metadata: Dict[str, Any]) -> None:
        metadata["content_type"] = self.content_type
        metadata["encoding"] = self.encoding
        metadata["transcoded_at"] = time()

    @abstractmethod
    def process(self, item: Any) -> Iterator[Any]: # Update to Iterator!
        """The specific logic for conversion (e.g. yield json.loads)."""
        pass