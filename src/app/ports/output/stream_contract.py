#
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
            # Basic runtime type enforcement
            if not isinstance(value, field_type):
                raise TypeError(
                    f"Contract Violation: '{field_name}' expects {field_type}, "
                    f"but got {type(value).__name__} ('{value}')"
                )
