# /srv/pipeline/src/app/middleware/telemetry.py
from typing import Any, Dict, Iterator
from src.app.ports.envelope import RegimeType
from src.app.ports.middleware import BaseMiddleware

class RowCounter(BaseMiddleware):
    """Counts the number of logical units passing through the pipeline."""
    
    def __init__(self, regime:RegimeType|str = RegimeType.ANY):
        super().__init__(input_regime=regime, output_regime=regime)
        self.count = 0
    
    def process(self, payload: Any) -> Iterator[Any]:
        # Increment internal state
        self.count += 1
        
        # Generator requirement: yield the payload to keep the pipe flowing
        yield payload
    
    def metadata_hook(self, metadata: Dict[str, Any]) -> None:
        # We use count + 1 so the metadata reflects the current object index
        metadata["pipeline_count_id"] = self.count + 1