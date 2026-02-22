# /srv/pipeline/src/app/middleware/telemetry.py
import time
from typing import Any
from datetime import timedelta
    

class RowCounter:
    """Counts the number of rows/chunks in the processed data"""
    def __init__(self):
        self.count = 0
    def __call__(self, item: Any) -> Any:
        self.count += 1
        return item # Always return the item so the chain continues!
    
class ExecutionTimer:
    def __init__(self):
        """Calculates start, end, and duration of process in pipeline"""
        self.start_time: float = 0.0
        self.end_time: float = 0.0

    def __call__(self, item: Any) -> Any:
        # Start the clock on the first chunk
        if self.start_time == 0.0:
            self.start_time = time.perf_counter()
        
        # We update end_time on every chunk; 
        # the last update will be the true finish time.
        self.end_time = time.perf_counter()
        return item

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time
    
    @property
    def readable_time(self) -> str:
        return str(timedelta(seconds=self.duration))