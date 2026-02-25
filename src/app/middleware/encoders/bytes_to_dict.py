# src/app/middleware/encoders/bytes_to_dict.py

import json
from typing import Iterator
from src.app.ports.middleware import EncoderMiddleware
from src.app.ports.envelope import RegimeType

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