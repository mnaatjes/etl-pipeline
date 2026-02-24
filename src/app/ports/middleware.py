# /srv/pipeline/src/app/ports/middleware.py
from time import time
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
from src.app.ports.envelope import Envelope, RegimeType

class BaseMiddleware(ABC):
    """The absolute base for all pipeline processors."""
    @abstractmethod
    def __call__(self, envelope: Envelope) -> Optional[Envelope]:
        """All middleware expects and returns an Envelope DTO"""
        pass

    def metadata_hook(self, metadata: Dict[str, Any]) -> None:
        """
        Optional hook. Subclasses override this to read or add metadata.
        - DO NOT overwrite dict using: metadata={'key':'val'}
        - DO USE: metadata['key'] = 'val'
        """
        pass

class ByteMiddleware(BaseMiddleware):
    """Contract: Input and Output must be bytes."""
    def __call__(self, envelope: Envelope) -> Optional[Envelope]:
        # Regime guard
        if envelope.regime != "BYTES":
            raise TypeError(
                f"{self.__class__.__name__} expects 'BYTES' regime, "
                f"Envelope is labeled: '{envelope.regime}'"
            )
        
        # Metadata Hook
        # Metadata dict passed By-Reference!!!
        self.metadata_hook(envelope.metadata)

        # Deligate to implementation method
        processed_payload = self.process(envelope.payload)

        # Filter Check
        if processed_payload is None:
            return None # filtered out
        
        # Repack payload
        envelope.payload = processed_payload
        return envelope

    @abstractmethod
    def process(self, item: bytes) -> Optional[bytes]:
        """Intake bytes from envelope.payload with regime BYTES"""
        pass

    def metadata_hook(self, metadata: Dict[str, Any]) -> None:
        """
        Optional hook. Subclasses override this to read or add metadata.
        - DO NOT overwrite dict using: metadata={'key':'val'}
        - DO USE: metadata['key'] = 'val'
        """
        pass

class ObjectMiddleware(BaseMiddleware):
    """
    Contract: Input and Output must be structured objects (dicts/lists).
    Standardizes payload extraction for high-level data manipulation.
    """
    def __call__(self, envelope: Envelope) -> Optional[Envelope]:
        # Regime guard
        if envelope.regime != "OBJECT":
            raise TypeError(
                f"{self.__class__.__name__} expects 'OBJECT' regime, "
                f"Envelope is labeled: '{envelope.regime}'"
            )
        
        # Metadata Hook
        # Metadata dict passed By-Reference!!!
        self.metadata_hook(envelope.metadata)

        # Deligate to implementation method
        processed_payload = self.process(envelope.payload)

        # Filter Check
        if processed_payload is None:
            return None # filtered out
        
        # Repack payload
        envelope.payload = processed_payload
        return envelope

    @abstractmethod
    def process(self, item: dict|list) -> Optional[dict|list]:
        """Intake bytes from envelope.payload with regime OBJECT"""
        pass

    def metadata_hook(self, metadata: Dict[str, Any]) -> None:
        """
        Optional hook. Subclasses override this to read or add metadata.
        - DO NOT overwrite dict using: metadata={'key':'val'}
        - DO USE: metadata['key'] = 'val'
        """
        pass

class EncoderMiddleware(BaseMiddleware):
    # Explicitly type attributes
    input_regime: RegimeType
    output_regime: RegimeType
    def __init__(
            self,
            input_regime: RegimeType,
            output_regime: RegimeType,
            content_type:str = "application/octet-stream",
            encoding:str = "utf-8"
    ) -> None:
        self.input_regime = input_regime
        self.output_regime = output_regime
        self.content_type = content_type
        self.encoding = encoding

    def __call__(self, envelope: Envelope) -> Optional[Envelope]:
        # 1. Guard the Input
        if envelope.regime != self.input_regime:
            raise TypeError(
                f"{self.__class__.__name__} expects '{self.input_regime}', "
                f"got '{envelope.regime}'"
            )

        # 2. Automatically Update Metadata (The Passport Stamp)
        self.metadata_hook(envelope.metadata)

        # 3. Transform (Implemented by subclass)
        processed_payload = self.process(envelope.payload)

        if processed_payload is None:
            return None

        # 4. Flip the Regime Label
        envelope.payload = processed_payload
        envelope.regime = self.output_regime
        
        return envelope

    def metadata_hook(self, metadata: Dict[str, Any]) -> None:
        """Standardizes the metadata stamp for all encoders."""
        metadata["content_type"] = self.content_type
        metadata["encoding"] = self.encoding
        metadata["transcoded_at"] = time()

    @abstractmethod
    def process(self, item: Any) -> Any:
        """The specific logic for conversion (e.g. json.loads)."""
        pass