# src/infrastructure/adapters/http/contract.py
from dataclasses import dataclass, field
from typing import Any
from src.app.ports.output.stream_contract import StreamContract
from src.infrastructure.adapters.http.enums import HttpReadMode

@dataclass(frozen=True)
class HttpContract(StreamContract):
    """Settings for HTTP/HTTPS adapter"""
    # Required Props
    chunk_size:int=1024
    use_lines:bool=False
    # HTTP Props
    read_mode:HttpReadMode = HttpReadMode.BYTES
    method:str="GET"
    timeout:float=30.0
    retries:int=3
    verify_ssl:bool=True
    headers:dict=field(default_factory=dict)
    user_agent:str="ED-Pipeline/1.0"
    request_body: Any | None = None
    params:dict=field(default_factory=dict)

    def __post_init__(self):
        # Triggers prop[type]:value validation
        super().__post_init__()

        # Validate Timeout
        # Ensure timeout is always a float, even if it came from YAML as an int
        if not isinstance(self.timeout, float):
            object.__setattr__(self, 'timeout', float(self.timeout))
        if self.timeout <=0: 
            raise ValueError(f"HTTP timeout must be positive float")
        
        # Safe headers merger
        input_headers = dict(self.headers)
        if "User-Agent" not in input_headers:
            input_headers["User-Agent"] = self.user_agent

        # Ensure http method declared
        # - Normalize to uppercase
        # - Assign after frozen
        object.__setattr__(self, 'method', self.method.upper())
        allowed = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"}
        if self.method not in allowed:
            raise ValueError(f"Unsupported HTTP method: {self.method}")
        
        # Apply to frozen instance via backdoor
        object.__setattr__(self, "headers", input_headers)