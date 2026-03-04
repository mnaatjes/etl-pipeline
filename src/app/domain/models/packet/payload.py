# src/app/domain/models/packet/payload.py
from typing import NewType

PayloadType = NewType("PayloadType", str)

class PayloadSubject:
    """
    The 'What' - Shared Vocabulary for Pipeline Packets.
    
    Acts as a descriptive label for the payload's state and schema.
    """
    BYTES   = PayloadType("binary:bytes")
    JSON    = PayloadType("document:json")
    DICT    = PayloadType("object:python-dict")
    CHUNK   = PayloadType("stream:chunk")
    VOID    = PayloadType("system:void")
