# src/app/pipelines/base.py
from typing import Generic, TypeVar, Iterable, Callable, List, Any
from ..ports.datastream import DataStream

class Pipeline:
    def __init__(
        self, 
        source: DataStream, 
        sink: DataStream,
        processors: List[Callable[[Any], Any]] = []
    ):
        self.source = source
        self.sink = sink
        self.processors = processors

    def run(self):
        """
        Orchestrates the flow between the Source and Sink DataStreams.
        This method manages the context of both streams automatically.
        """
        # 1. Open both streams using their __enter__ methods
        with self.source as src, self.sink as snk:
            
            # 2. Iterate through the source read generator
            for chunk in src.read():
                
                # 3. Pass chunk through the middleware chain
                processed_chunk = chunk
                for process in self.processors:
                    processed_chunk = process(processed_chunk)
                    if processed_chunk is None:
                        break
                
                # 4. If not filtered out, write to the sink
                if processed_chunk is not None:
                    snk.write(processed_chunk)