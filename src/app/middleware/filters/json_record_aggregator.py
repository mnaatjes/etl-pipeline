# src/app/middleware/filters/json_record_aggregator.py
from typing import Iterator
from src.app.ports.middleware import StatefulMiddleware
from src.app.ports.envelope import Envelope, RegimeType

class JsonRecordAggregator(StatefulMiddleware):
    """
    A Stateful Middleware that buffers byte fragments and yields 
    complete, logically-valid JSON objects based on brace-matching.
    """
    def __init__(self):
        # Explicitly define the linguistic transformation: BYTES to BYTES
        super().__init__(input_regime=RegimeType.BYTES, output_regime=RegimeType.BYTES)
        self._buffer = b""

    def process(self, payload: bytes) -> Iterator[bytes]:
        # 1. Accumulate the new fragment into the existing buffer
        self._buffer += payload

        # 2. THE LINGUISTIC SPLIT
        # We look for a closing brace followed by a potential separator (newline or comma)
        # Professional standard for pretty-printed arrays: '}\n' or '},'
        while b"}\n" in self._buffer or b"}," in self._buffer:
            # Determine which delimiter appeared first to maintain order
            idx_newline = self._buffer.find(b"}\n")
            idx_comma = self._buffer.find(b"},")
            
            # Pick the earliest occurrence
            if idx_newline != -1 and (idx_comma == -1 or idx_newline < idx_comma):
                split_at = idx_newline + 1 # Split after the '}'
            else:
                split_at = idx_comma + 1 # Split after the '}'

            # Slice the buffer: 'unit' is the complete object, 'self._buffer' is the remainder
            unit = self._buffer[:split_at]
            self._buffer = self._buffer[split_at:]

            # 3. CLEANING & VALIDATION
            # Strip structural array noise (like the leading '[' or trailing ',')
            clean_unit = unit.strip().strip(b"[").strip(b",").strip()
            
            if clean_unit.startswith(b"{") and clean_unit.endswith(b"}"):
                yield clean_unit