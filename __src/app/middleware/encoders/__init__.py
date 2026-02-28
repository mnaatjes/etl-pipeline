# src/app/middleware/encoders/__init__.py

"""
Encoder - i.e. Regime Changer - Middleware
- Should inherit directly from BaseMiddleware as they change the Envelope.regime property!
- From regimeA BYTES To regimeB OBJECT
"""

from .bytes_to_dict import BytesToDict
from .dict_to_bytes import DictToBytes

__all__ = [
    "BytesToDict",
    "DictToBytes"
]