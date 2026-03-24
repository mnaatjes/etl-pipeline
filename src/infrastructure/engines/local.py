from typing import Iterator, List
from src.app.ports.output.pipeline_engine import PipelineEngine
from src.app.domain.models.pipeline.blueprint import PipelineBlueprint
from src.app.domain.models.packet import Packet, FlowSignal
from src.app.domain.exceptions.pipeline.pipeline_execution_error import PipelineExecutionError

class LocalPipelineEngine(PipelineEngine):
    """
    A Sequential, Single-Threaded Execution Engine.
    
    Processes resources one-by-one, passing data through the 
    middleware chain and broadcasting to all sinks.
    """

    def setup(self, blueprint: PipelineBlueprint) -> 'LocalPipelineEngine':
        super().setup(blueprint)
        return self

    def execute(self) -> None:
        """
        The core execution loop.
        """
        if not self._blueprint:
            raise RuntimeError("Engine not setup.")

        try:
            # 1. OPEN ALL SINKS
            # We open sinks first to ensure we can write as soon as data arrives.
            for sink in self._blueprint.sinks:
                sink.__enter__()

            # 2. PROCESS SOURCES SEQUENTIALLY
            for source in self._blueprint.sources:
                with source as stream:
                    for packet in stream.read():
                        # Pass through the processor chain
                        self._dispatch_to_sinks(packet)

            # 3. FINALIZATION (FLUSH)
            # After all sources are done, trigger flush() on all processors
            self._trigger_flush()

        except Exception as e:
            raise PipelineExecutionError(f"Local Execution Failed: {e}") from e
        finally:
            # 4. SHUTDOWN
            self.shutdown()

    def shutdown(self) -> None:
        """Ensures all resources are closed."""
        if self._blueprint:
            for sink in self._blueprint.sinks:
                sink.__exit__(None, None, None)
        super().shutdown()

    # --- INTERNAL ORCHESTRATION ---

    def _dispatch_to_sinks(self, packet: Packet) -> None:
        """Pipes a single packet through processors and into all sinks."""
        if not self._blueprint: return
        
        processors = self._blueprint.processors
        sinks = self._blueprint.sinks

        def process_recursive(p: Packet, index: int):
            if index >= len(processors):
                # Broadcast to all sinks
                for sink in sinks:
                    sink.write(p.payload)
                return

            processor = processors[index]
            for processed_packet in processor.process(p):
                process_recursive(processed_packet, index + 1)

        process_recursive(packet, 0)

    def _trigger_flush(self) -> None:
        """Triggers the flush signal through the entire chain."""
        if not self._blueprint: return
        
        processors = self._blueprint.processors

        def flush_recursive(index: int):
            if index >= len(processors):
                # No more processors to flush
                return

            processor = processors[index]
            # 1. Flush this processor
            for flushed_packet in processor.flush():
                # 2. Pipe flushed results through the REMAINING chain
                self._dispatch_to_remaining_sinks(flushed_packet, index + 1)
            
            # 3. Move to next processor in the chain
            flush_recursive(index + 1)

        flush_recursive(0)

    def _dispatch_to_remaining_sinks(self, packet: Packet, start_index: int) -> None:
        """Helper to pipe a flushed packet through the rest of the chain."""
        if not self._blueprint: return

        processors = self._blueprint.processors
        sinks = self._blueprint.sinks

        def process_recursive(p: Packet, index: int):
            if index >= len(processors):
                for sink in sinks:
                    sink.write(p.payload)
                return

            processor = processors[index]
            for processed_packet in processor.process(p):
                process_recursive(processed_packet, index + 1)

        process_recursive(packet, start_index)
