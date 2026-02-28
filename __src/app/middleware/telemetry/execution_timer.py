# /srv/pipeline/src/app/middleware/telemetry.py
import time
from typing import Any, Dict, Iterator
from datetime import timedelta
from src.app.ports.envelope import RegimeType
from src.app.ports.middleware import BaseMiddleware

class ExecutionTimer(BaseMiddleware):
    """Calculates start, end, and duration of the pipeline execution."""

    def __init__(self):
        super().__init__(input_regime=RegimeType.ANY, output_regime=RegimeType.ANY)

        self.start_time: float = 0.0
        self.end_time: float = 0.0

    def process(self, payload: Any) -> Iterator[Any]:
        now = time.perf_counter()
        
        # Initialize start_time on the very first unit that hits this middleware
        if self.start_time == 0.0:
            self.start_time = now

        # Record the most recent pulse
        self.end_time = now
        
        yield payload
    
    def metadata_hook(self, metadata: Dict[str, Any]) -> None:
        # Arrival timestamp for this specific unit
        metadata["arrival_timestamp"] = time.perf_counter()

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time
    
    @property
    def readable_time(self) -> str:
        # Converts duration (float) to a human-readable HH:MM:SS format
        return str(timedelta(seconds=self.duration))