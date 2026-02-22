# /srv/pipeline/src/app/middleware/security.py

import hashlib
from typing import Any
from ..ports.middleware import ByteMiddleware

class SHA256Hasher(ByteMiddleware):
    def __init__(self):
        self._sha256 = hashlib.sha256()

    def process(self, item:bytes) -> bytes:
        # Ensure we are hashing bytes. 
        # If your middleware up-leveled to dict, you'd need to re-encode to bytes here.
        if isinstance(item, bytes):
            self._sha256.update(item)
        return item

    def get_hash(self) -> str:
        return self._sha256.hexdigest()