# src/app/middleware/encoders/dict_to_bytes.py
import json
from typing import Iterator
from src.app.ports.middleware import EncoderMiddleware
from src.app.ports.envelope import RegimeType
        
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