# src/app/ports/settings.py
from abc import ABC
from dataclasses import dataclass

@dataclass(frozen=True)
class StreamContract(ABC):
    """
    - Interface 
    - Every STREAM must have certain properties
    - Blueprint Only
    """
    chunk_size:int
    use_lines:bool = False