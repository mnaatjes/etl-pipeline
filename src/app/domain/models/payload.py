# src/app/domain/models/payload.py
from typing import NewType

PayloadType = NewType("PayloadType", str)

class Subject:
    """Shared Vocabulary for Pipeline Packets"""
    BYTES   = PayloadType("binary:bytes")
    JSON    = PayloadType("document:json")
    DICT    = PayloadType("object:python-dict")
    CHUNK   = PayloadType("stream:chunk")
    VOID    = PayloadType("system:void")