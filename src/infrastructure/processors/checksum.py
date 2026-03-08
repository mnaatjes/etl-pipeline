import hashlib
from typing import Iterator
from src.app.ports.output.middleware_processor import MiddlewareProcessor
from src.app.domain.models.packet import Packet, PayloadType, PayloadSubject

class ChecksumProcessor(MiddlewareProcessor):
    """
    A 1:1 Pass-Through Processor that calculates the checksum of a byte stream.
    Useful for validating large downloads (e.g. 200GB json.gz) in real-time.
    """
    def __init__(self, algorithm: str = "sha256"):
        self._hash = hashlib.new(algorithm)
        self._total_bytes = 0
        self._algorithm = algorithm

    @property
    def input_subject(self) -> PayloadType: 
        return PayloadSubject.BYTES
    
    @property
    def output_subject(self) -> PayloadType: 
        return PayloadSubject.BYTES

    def process(self, packet: Packet) -> Iterator[Packet]:
        """
        Updates the internal hash with the current chunk and yields it immediately.
        """
        if packet.payload:
            self._hash.update(packet.payload)
            self._total_bytes += len(packet.payload)

        # Pass-through for the next stage (e.g. a File Sink)
        yield packet

    def flush(self) -> Iterator[Packet]:
        """No final buffering required."""
        yield from []

    @property
    def digest(self) -> str:
        """Returns the current hexadecimal digest."""
        return self._hash.hexdigest()

    @property
    def total_bytes(self) -> int:
        """Returns the count of bytes processed so far."""
        return self._total_bytes
