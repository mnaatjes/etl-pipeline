# src/app/ports/output/stream_contract.py
from typing import Any, get_origin, Union
import typing
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
    
    def __post_init__(self):
        """Universal Type Guard for all Contracts."""
        for field_name, field_type in self.__annotations__.items():
            value = getattr(self, field_name)
            
            # 1. Robust check for Any and 'Special Forms' (Union, Optional, etc.)
            # We check the object, its string name, and its origin.
            if (
                field_type is Any or 
                field_type is typing.TypeVar or
                str(field_type).endswith("Any") or
                get_origin(field_type) in (Union, list, dict, tuple) or
                str(type(field_type)).lower().find("specialform") != -1
            ):
                continue

            # 2. Flexible Numeric Check
            if field_type is float and isinstance(value, (int, float)):
                continue

            # 3. Final Safety: Only run isinstance if field_type is a concrete class
            if isinstance(field_type, type):
                if not isinstance(value, field_type):
                    raise TypeError(
                        f"Contract Violation: '{field_name}' expects {field_type}, "
                        f"but got {type(value).__name__} ('{value}')"
                    )
