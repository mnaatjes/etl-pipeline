# src/app/middleware/encoders.py
import io
import json
import csv
from typing import Dict, Optional, Any, Iterator
from src.app.ports.middleware import EncoderMiddleware
from src.app.ports.envelope import Envelope, RegimeType

"""
Encoder - i.e. Regime Changer - Middleware
- Should inherit directly from BaseMiddleware as they change the Envelope.regime property!
- From regimeA BYTES To regimeB OBJECT
"""
class BytesToDict(EncoderMiddleware):
    """
    Inbound Bridge: Transforms raw BYTES into a Python Dictionary (OBJECT).
    Assumes the incoming byte chunk is a single, complete logical unit.
    """
    def __init__(self, encoding: str = "utf-8"):
        super().__init__(
            input_regime=RegimeType.BYTES,
            output_regime=RegimeType.OBJECT,
            content_type="application/x-python-dict",
            encoding=encoding
        )

    def process(self, payload: bytes) -> Iterator[dict]:
        """
        Parses bytes to dict. 
        Note: We yield the result to satisfy the Iterator contract.
        """
        try:
            # 1. Decode bytes to string
            decoded_str = payload.decode(self.encoding)
            
            # 2. Parse JSON
            result = json.loads(decoded_str)

            # 3. Validation: Ensure we actually got a dictionary
            if not isinstance(result, dict):
                # If it's a list or other type, we skip it or raise error
                # For our pipeline, we expect one object per 'Baton'
                return 

            yield result

        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            # In a production environment, you might log this 
            # or yield a 'Dead Letter' envelope instead of crashing.
            raise ValueError(f"Failed to parse JSON unit: {e}") from e
        
class DictToBytes(EncoderMiddleware):
    """
    Outbound Bridge: Transforms a Python Dictionary (OBJECT) back into BYTES.
    Standardizes serialization for sinks that require binary data.
    """
    def __init__(self, encoding: str = "utf-8", indent: int = 4):
        super().__init__(
            input_regime=RegimeType.OBJECT,
            output_regime=RegimeType.BYTES,
            content_type="application/json",
            encoding=encoding
        )
        self.indent = indent

    def process(self, payload: dict) -> Iterator[bytes]:
        """
        Serializes a dictionary to JSON bytes.
        """
        try:
            # 1. Serialize dict to string
            # We use separators to ensure compact output if no indent is provided
            json_str = json.dumps(
                payload, 
                indent=self.indent, 
                ensure_ascii=False,
                separators=(",", ":") if self.indent is None else None
            )
            
            # 2. Encode string to bytes
            yield json_str.encode(self.encoding)

        except (TypeError, ValueError) as e:
            # Handles cases where the payload might contain non-serializable objects
            raise ValueError(f"Serialization failed for unit: {e}") from e