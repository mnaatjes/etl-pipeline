# src/app/middelware/__init__.py

"""
src/app/middleware/
├── __init__.py
├── encoders.py       # "Regime" changes (JSON to Bytes, Dict to Msgpack)
├── filters.py        # Logic that returns None to skip records (Dropping nulls, schema validation)
├── logic.py          # Business/Domain logic (Calculating taxes, mapping keys, renaming)
├── security.py       # Encryption, hashing (SHA256), and PII masking
└── telemetry.py      # Side-effects (Row counters, progress bars, logging)
"""

from . import telemetry as metrics
from . import encoders as convert
from . import security as auth

__all__ = ["metrics", "convert", "auth"]
