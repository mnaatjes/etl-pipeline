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
        Standardizes the data flow using Generator-based Middlewares.
        Handles 1-to-0, 1-to-1, and 1-to-Many data transformations.
        """
        with self.source as src, self.sink as snk:
        # 1. Start the Source Stream
            for source_envelope in src.read():
                
                # 2. Initialize the 'Working Set' for this specific chunk
                # We wrap the source envelope in a list to start the chain
                working_set = [source_envelope]

                # 3. Iterate through the Middleware Chain
                for processor in self.processors:
                    next_set = []
                    
                    # Each processor consumes the current working set
                    for env in working_set:
                        # 'processor(env)' is now a generator/iterator
                        for processed_env in processor(env):
                            # Collect all outputs (0, 1, or Many)
                            next_set.append(processed_env)
                    
                    # The output of this processor becomes the input for the next
                    working_set = next_set

                    # Optimization: If the set is empty, stop processing this chunk
                    if not working_set:
                        break
            
                # 4. Final delivery to the Sink
                for final_envelope in working_set:
                    snk.write(final_envelope)