# src/infrastructure/adapters/http/contract.py

from dataclasses import dataclass, field
from src.app.ports.output.stream_contract import StreamContract

@dataclass(frozen=True)
class HttpContract(StreamContract):
    """Settings for HTTP/HTTPS adapter"""
    # Required Props
    chunk_size:int=1024
    use_lines:bool=False
    # HTTP Props
    timeout:int=30
    retries:int=3
    verify_ssl:bool=True
    headers:dict=field(default_factory=dict)
    user_agent:str="ED-Pipeline/1.0"

    def __post_init__(self):
        # Triggers prop[type]:value validation
        super().__post_init__()

        if self.timeout <=0: raise ValueError(f"HTTP timeout must be positive int")
        
        # Safe headers merger
        input_headers = dict(self.headers)
        if "User-Agent" not in input_headers:
            input_headers["User-Agent"] = self.user_agent
        
        # Apply to frozen instance via backdoor
        object.__setattr__(self, "headers", input_headers)