# src/app/middleware/security.py

from typing import Any, Dict, Iterator
from src.app.ports.middleware import BaseMiddleware

class ContentTypeGuard(BaseMiddleware):
    def __init__(self, expected_type: str = "application/json"):
        # We want to check this as early as possible (BYTES regime)
        super().__init__(input_regime="ANY", output_regime="ANY")
        self.expected_type = expected_type
        self._verified = False

    def process(self, payload: Any) -> Iterator[Any]:
        yield payload

    def metadata_hook(self, metadata: Dict[str, Any]) -> None:
        if not self._verified:
            # Check the header injected by your decorator
            actual_type = metadata.get("content-type") or metadata.get("Content-Type")
            
            if actual_type and self.expected_type not in actual_type:
                raise RuntimeError(
                    f"SECURITY ALERT: Expected {self.expected_type}, "
                    f"but source sent {actual_type}. Aborting stream."
                )
            self._verified = True