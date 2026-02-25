# src/app/middleware/telemetry.py

from typing import Iterator, Any, Dict, List
from src.app.ports.middleware import BaseMiddleware
from src.app.ports.envelope import RegimeType, Envelope

class HttpHeaderInspector(BaseMiddleware):
    """
    Observability Middleware: Prints specific metadata/headers 
    injected by Decorators or previous Middlewares.
    """
    def __init__(self, interesting_headers: List[str]|None = None):
        # We are agnostic; we can inspect headers at any stage
        super().__init__(input_regime=RegimeType.ANY, output_regime=RegimeType.ANY)
        # If no specific headers provided, we'll watch for common ones
        self.watch_list = interesting_headers or [
            "Content-Type", 
            "Content-Length", 
            "Server", 
            "Last-Modified"
        ]
        self._has_logged_summary = False

    def process(self, payload: Any) -> Iterator[Any]:
        # Pass-through: Just keep the stream moving
        yield payload

    def metadata_hook(self, metadata: Dict[str, Any]) -> None:
        if not self._has_logged_summary:
            print("\n" + "="*40)
            print("  [DEBUG] INBOUND RESOURCE HEADERS")
            print("-" * 40)
            
            found_any = False
            for key in self.watch_list:
                # 1. Try exact match, then lowercase match
                val = metadata.get(key) or metadata.get(key.lower())
                
                # 2. If we found a value either way, print it
                if val is not None:
                    print(f"  {key:<15}: {val}")
                    found_any = True
            
            if not found_any:
                print("  ! No watched headers found in metadata.")
                # For debugging, maybe print the first few raw keys found:
                # print(f"  DEBUG: Raw keys in metadata: {list(metadata.keys())[:5]}")
                
            print("="*40 + "\n")
            self._has_logged_summary = True