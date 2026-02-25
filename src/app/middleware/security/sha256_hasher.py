import hashlib
from typing import Iterator
from src.app.ports.middleware import ByteMiddleware

class Sha256Hasher(ByteMiddleware):
    """
    Calculates a running SHA256 checksum of the byte stream.
    Does not modify the payload; passes it through exactly as is.
    """
    def __init__(self):
        super().__init__()
        self._sha256 = hashlib.sha256()

    def process(self, payload: bytes) -> Iterator[bytes]:
        # 1. Update the running hash state with the new chunk
        self._sha256.update(payload)
        
        # 2. Yield the payload unchanged (Pass-through)
        yield payload

    @property
    def hex_digest(self) -> str:
        """Return the final checksum as a hex string."""
        return self._sha256.hexdigest()