import msgpack
import json
from typing import Any, cast

class JsonToMsgpackProcessor:
    """
    Regime: JSON Bytes -> Python Object -> Msgpack Binary
    """
    def __call__(self, chunk: bytes) -> bytes:
        # 1. Parse JSON
        try:
            data = json.loads(chunk.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # If the chunk isn't valid JSON, we return an empty byte string 
            # or handle it as your policy dictates.
            return b""
        
        # 2. Serialize to Msgpack
        packed = msgpack.packb(data, use_bin_type=True)
        
        # 3. Type Guard: Ensure we actually have bytes before returning
        if packed is None:
            return b""
            
        return cast(bytes, packed)

class RawToHexProcessor:
    """
    Regime: Any -> Hexadecimal String (as bytes)
    Useful for debugging 'binary' outputs in a text editor.
    """
    def __call__(self, data: Any) -> bytes:
        if isinstance(data, dict):
            data = json.dumps(data).encode('utf-8')
        return data.hex().encode('utf-8')