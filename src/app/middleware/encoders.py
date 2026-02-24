# src/app/middleware/encoders.py
import io
import json
import csv
from typing import Dict, Optional, Any
from src.app.ports.middleware import EncoderMiddleware
from src.app.ports.envelope import Envelope

"""
Encoder - i.e. Regime Changer - Middleware
- Should inherit directly from BaseMiddleware as they change the Envelope.regime property!
- From regimeA BYTES To regimeB OBJECT
"""

class JsonToBytes(EncoderMiddleware):
    def __init__(self):
        super().__init__(
            input_regime="OBJECT",
            output_regime="BYTES",
            content_type="application/json"
        )

    def process(self, item:dict|list) -> bytes:
        return json.dumps(item).encode(self.encoding)

class BytesToJson(EncoderMiddleware):
    def __init__(self) -> None:
        super().__init__(
            input_regime="BYTES",
            output_regime="OBJECT",
            content_type="application/json"
        )
    
    def process(self, item:bytes) -> dict|list:
        # serialize
        return json.loads(item.decode(self.encoding))
    
class BytesToDict(EncoderMiddleware):
    def __init__(self):
        super().__init__(
            input_regime="BYTES",
            output_regime="OBJECT",
            content_type="application/x-python-dict"
        )
    
    def process(self, item:bytes) -> dict:
        result = json.loads(item.decode(self.encoding))
        # Validate and Return
        if not isinstance(result, dict):
            raise TypeError(f"Expected 'dict' from JSON, received: '{type(result).__name__}'")
        return result

class DictToBytes(EncoderMiddleware):
    def __init__(self):
        super().__init__(
            input_regime="OBJECT",
            output_regime="BYTES",
            content_type="application/octet-stream"
        )

    def process(self, item: dict) -> bytes:
        # You could use json, or even pickle/msgpack here if needed
        return json.dumps(item).encode(self.encoding)