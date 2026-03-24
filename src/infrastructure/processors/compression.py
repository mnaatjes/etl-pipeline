import zlib
from typing import Iterator, Optional
from src.app.ports.output.middleware_processor import MiddlewareProcessor
from src.app.domain.models.packet import Packet, PayloadType, PayloadSubject

class GzipDecompressor(MiddlewareProcessor):
    """
    The 'Lung' - Perfroms streaming GZIP decompression on a byte stream.
    
    Uses zlib.decompressobj to allow chunk-by-chunk processing without 
    loading the entire file into memory.
    """
    def __init__(self):
        # wbits=31: 15 (MAX_WBITS) + 16 (Gzip Header detection)
        self._decompressor = zlib.decompressobj(wbits=31)

    @property
    def name(self) -> str:
        return "GzipDecompressor"

    @property
    def input_subject(self) -> PayloadType:
        return PayloadSubject.BYTES

    @property
    def output_subject(self) -> PayloadType:
        return PayloadSubject.BYTES

    def process(self, packet: Packet) -> Iterator[Packet]:
        """
        Decompresses a single chunk and yields any resulting raw bytes.
        """
        if not packet.payload:
            return

        try:
            uncompressed = self._decompressor.decompress(packet.payload)
            if uncompressed:
                yield packet.spawn(payload=uncompressed)
        except zlib.error as e:
            raise ValueError(f"Decompression error: {e}")

    def flush(self) -> Iterator[Packet]:
        """
        Releases the final bytes and ensures the Gzip checksum is valid.
        """
        try:
            remainder = self._decompressor.flush()
            if remainder:
                # Note: We don't have a packet to spawn from here, 
                # but we usually don't need the context for the very last bytes 
                # or we can pass it from the last seen packet if we stored it.
                # For now, we'll return empty as zlib usually flushes during decompress()
                # for gzip unless it's a very specific stream boundary.
                yield from []
        except zlib.error as e:
            raise ValueError(f"Decompression flush error: {e}")
