import ijson
import io
import threading
import queue
from typing import Iterator, List, Any
from src.app.ports.output.middleware_processor import MiddlewareProcessor
from src.app.domain.models.packet import Packet, PayloadType, PayloadSubject

class IterableToFileAdapter:
    """
    Adapts an iterator of bytes into a file-like object with a read() method.
    """
    def __init__(self, iterable: Iterator[bytes]):
        self.iterator = iterable
        self.buffer = b""

    def read(self, size: int = -1) -> bytes:
        while not self.buffer:
            try:
                self.buffer = next(self.iterator)
            except StopIteration:
                return b""
        
        if size < 0 or size >= len(self.buffer):
            res = self.buffer
            self.buffer = b""
            return res
        
        res = self.buffer[:size]
        self.buffer = self.buffer[size:]
        return res

class JsonStreamProcessor(MiddlewareProcessor):
    """
    The 'Brain' - Performs streaming JSON parsing.
    
    Uses ijson to yield complete Python dictionaries from a byte stream.
    This processor is a 'Regime Changer': it converts BYTES into DICT.
    """
    def __init__(self, map_path: str = "item"):
        """
        :param map_path: The ijson path to the objects (e.g., 'item' for a list of objects).
        """
        self._map_path = map_path
        self._input_queue = queue.Queue()
        self._output_queue = queue.Queue()
        self._thread = None
        self._last_packet = None

    @property
    def name(self) -> str:
        return "JsonStreamProcessor"

    @property
    def input_subject(self) -> PayloadType:
        return PayloadSubject.BYTES

    @property
    def output_subject(self) -> PayloadType:
        return PayloadSubject.DICT

    def _run_parser(self):
        """Background thread that drives the ijson pull-parser."""
        def source_iterator():
            while True:
                chunk = self._input_queue.get()
                if chunk is None: # Sentinel
                    break
                yield chunk

        try:
            # Wrap the iterator in a file-like adapter
            file_like = IterableToFileAdapter(source_iterator())
            
            # ijson.items yields the objects
            for item in ijson.items(file_like, self._map_path):
                self._output_queue.put(item)
        except Exception as e:
            self._output_queue.put(e)
        finally:
            self._output_queue.put(StopIteration)

    def process(self, packet: Packet) -> Iterator[Packet]:
        """
        Receives byte chunks, pushes them to the parser, and yields any complete objects.
        """
        self._last_packet = packet
        
        # 1. Lazy-start the parser thread
        if self._thread is None:
            self._thread = threading.Thread(target=self._run_parser, daemon=True)
            self._thread.start()

        # 2. Push chunk into the parser's mouth
        self._input_queue.put(packet.payload)

        # 3. Yield any objects that popped out of the brain
        while not self._output_queue.empty():
            item = self._output_queue.get_nowait()
            if isinstance(item, Exception):
                raise item
            if item is StopIteration:
                break
            
            # Spawn a new packet with DICT subject
            yield packet.spawn(payload=item, subject=PayloadSubject.DICT)

    def flush(self) -> Iterator[Packet]:
        """
        Signifies end of stream to the parser and yields final objects.
        """
        if self._thread is None:
            return

        # 1. Signal end of stream
        self._input_queue.put(None)
        
        # 2. Wait for parser to finish and drain output
        self._thread.join(timeout=5.0)
        
        while not self._output_queue.empty():
            item = self._output_queue.get_nowait()
            if item is StopIteration or isinstance(item, Exception):
                continue
            
            if self._last_packet:
                yield self._last_packet.spawn(payload=item, subject=PayloadSubject.DICT)
