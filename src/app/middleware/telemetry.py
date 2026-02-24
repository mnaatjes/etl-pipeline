# /srv/pipeline/src/app/middleware/telemetry.py
import time
from typing import Any, Dict
from datetime import timedelta
from src.app.ports.envelope import Envelope
from src.app.ports.middleware import BaseMiddleware
"""
Regime Agnostic Middleware
"""
    

class RowCounter(BaseMiddleware):
    """Counts the number of rows/chunks in the processed data"""
    def __init__(self):
        self.count = 0
    
    def __call__(self, envelope:Envelope) -> Envelope:
        # Increment property
        self.count += 1
        # Handle metadata
        self.metadata_hook(envelope.metadata)
        # Return Envelope
        return envelope
    
    def metadata_hook(self, metadata: Dict[str, Any]) -> None:
        metadata["pipeline_count_id"] = self.count


class ExecutionTimer(BaseMiddleware):
    def __init__(self):
        """Calculates start, end, and duration of process in pipeline"""
        self.start_time: float = 0.0
        self.end_time: float = 0.0

    def __call__(self, envelope:Envelope) -> Envelope:
        # Init Start time
        now = time.perf_counter()
        if self.start_time == 0.0:
            self.start_time = now

        # Update End Time
        self.end_time = now

        # Handle metadata
        self.metadata_hook(envelope.metadata, now)
        # Return Envelope
        return envelope
    
    def metadata_hook(self, metadata: Dict[str, Any], timestamp: float) -> None:
        # Record the precise moment this chunk hit this specific telemetry point
        metadata["arrival_timestamp"] = timestamp

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time
    
    @property
    def readable_time(self) -> str:
        return str(timedelta(seconds=self.duration))