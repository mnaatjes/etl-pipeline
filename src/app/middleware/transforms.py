import json
from typing import Any

class JsonDeserializer:
    """Converts raw bytes from the stream into a Python List/Dict."""
    def __call__(self, chunk: bytes) -> Any:
        # NOTE: In a real streaming scenario with large files, 
        # you'd use a streaming parser like 'ijson'.
        # For this example, we assume the chunk is a complete JSON string.
        return json.loads(chunk.decode('utf-8'))

class JsonSerializer:
    """Converts a Python List/Dict back into bytes for the Sink."""
    def __call__(self, data: Any) -> bytes:
        return json.dumps(data).encode('utf-8')

def uppercase_titles(data: list) -> list:
    """A sample Domain Transformation (ETL)."""
    for item in data:
        if 'title' in item:
            item['title'] = item['title'].upper()
    return data

class StreamBuffer:
    """
    Collects all chunks into a single byte-string.
    Note: Only use this for files that fit in your RAM (like JSONPlaceholder).
    """
    def __init__(self):
        self.buffer = b""

    def __call__(self, chunk: bytes) -> bytes | None:
        self.buffer += chunk
        # We return None so the Pipeline loop 'breaks' and doesn't 
        # try to write partial data to the sink yet.
        return None

    def get_full_data(self) -> bytes:
        return self.buffer