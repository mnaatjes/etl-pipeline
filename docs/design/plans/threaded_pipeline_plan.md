# Threaded Pipeline Engine 

Implementing a ThreadedPipelineEngine allows you to leverage your Linux server's multi-core capabilities while maintaining the resource "guardrails" defined in your abstract base class.

Since your DuckDBSchemaProcessor creates a unique in-memory connection per file, each thread will operate in its own isolated memory space, making this highly efficient for I/O-bound tasks.

**Implementation: ThreadedPipelineEngine**

```py
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from src.app.ports.output.pipeline_engine import PipelineEngine
from src.app.domain.models.pipeline.blueprint import PipelineBlueprint
from src.app.domain.exceptions.pipeline.pipeline_execution_error import PipelineExecutionError

class ThreadedPipelineEngine(PipelineEngine):
    """
    A concurrent execution strategy using a ThreadPool.
    Optimized for I/O tasks like reading JSON samples and writing SQL schemas.
    """
    
    def __init__(self, trace_id: str, max_workers: int = 4) -> None:
        super().__init__(trace_id)
        self.max_workers = max_workers
        self._executor: ThreadPoolExecutor = None

    def setup(self, blueprint: PipelineBlueprint) -> 'ThreadedPipelineEngine':
        """Initialize the blueprint and prepare the thread pool."""
        self._blueprint = blueprint
        # Pre-allocate the executor to manage the pool lifecycle
        self._executor = ThreadPoolExecutor(
            max_workers=self.max_workers, 
            thread_name_prefix=f"pipeline-{self.trace_id}"
        )
        return self

    def execute(self) -> None:
        """
        Orchestrates parallel execution of the pipeline processors.
        Uses a worker-pattern to pass each item through the processor chain.
        """
        if not self._blueprint:
            raise PipelineExecutionError("Engine execution failed: Setup was not called.")

        try:
            # 1. Fetch work items from the source (e.g., list of file paths)
            work_items = self._blueprint.source.read()

            # 2. Define the localized chain logic for a single thread
            def _process_item(item):
                current_data = item
                for processor in self._blueprint.processors:
                    current_data = processor.process(current_data)
                    if current_data is None:
                        break
                return current_data

            # 3. Dispatch tasks to the pool
            futures = [self._executor.submit(_process_item, item) for item in work_items]

            # 4. Monitor futures and handle task-level exceptions
            for future in as_completed(futures):
                try:
                    future.result() # Re-raises exceptions caught in the thread
                except Exception as task_err:
                    self.logger.error(f"Task failure in trace {self.trace_id}: {task_err}")
                    # You can choose to 'fail-fast' here or continue processing others
                    raise PipelineExecutionError(f"Pipeline task failed: {task_err}")

        except Exception as e:
            # Map any implementation-level errors to the domain exception
            raise PipelineExecutionError(f"Threaded engine failed to complete: {str(e)}")

    def shutdown(self) -> None:
        """
        Ensures the thread pool is closed and all resources are released.
        This is called automatically by the __exit__ method in your base class.
        """
        if self._executor:
            self._executor.shutdown(wait=True)
        
        super().shutdown()
```

How this manages your Resources
Concurrency Control (max_workers): By setting a limit (e.g., 4 or 8), you prevent the pipeline from overwhelming the Linux host's CPU or spawning too many simultaneous DuckDB memory allocations.

Thread-Local Isolation: Because each process() call in your DuckDBSchemaProcessor uses `duckdb.connect(':memory:')`, each thread gets a private database instance. There is no shared state to lock or corrupt.

Lifecycle Integrity: Because your PipelineEngine uses the __exit__ context manager, even if the script crashes or you hit Ctrl+C, the shutdown() method is guaranteed to run. This closes the thread pool and releases the RAM held by the Python thread handles.

I/O Efficiency: While one thread is waiting for the Linux kernel to finish writing a .sql file to disk, another thread can be using DuckDB to parse the next JSON sample.

Usage in your Main Entrypoint

```py
    # Setup the blueprint (Source + Processors)
    blueprint = PipelineBlueprint(source=my_source, processors=[schema_proc, manifest_proc])

    # Run within the context manager for safety
    engine = ThreadedPipelineEngine(trace_id="12345", max_workers=4)
    with engine.setup(blueprint) as runner:
        runner.execute()
```