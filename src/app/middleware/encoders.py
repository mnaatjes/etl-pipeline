# src/app/middleware/encoders.py

import json

class JsonToBytes:
    def __call__(self, data: dict) -> bytes:
        return json.dumps(data).encode('utf-8')