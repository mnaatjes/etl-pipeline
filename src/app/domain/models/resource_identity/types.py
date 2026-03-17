# src/app/domain/models/resource_identity.py/types.py
from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs
from enum import StrEnum
from typing import NewType, Dict

"""
ResourceKey:
- Nickname / Alias used to look-up anchor paths
- Extracted from the URI
- e.g. "scans"
"""
ResourceKey = NewType("ResourceKey", str)


@dataclass(frozen=True)
class ParsedURI:
    """Dataclass representing a parsed URI used by ResourceIdentity"""
    protocol:str
    authority:str
    path:str
    query:Dict[str,str] = field(default_factory=dict)

    @classmethod
    def from_string(cls, uri:str) -> 'ParsedURI':
        # Validate
        if not "://" in uri:
            return cls(
                protocol="",
                authority="",
                path=uri
            )
        
        # Split and Parse
        parsed      = urlparse(uri)
        query_map   = {k: v[0] for k, v in parse_qs(parsed.query).items()}

        # Return Parsed URI
        return cls(
            protocol=parsed.scheme,
            authority=parsed.netloc,
            path=parsed.path,
            query=query_map
        )
    
class Realm(StrEnum):
    """Classification of Resource Environments"""
    LOCAL       = "local"
    NETWORK     = "network"
    MEMORY      = "memory"
    SYNTHETIC   = "synthetic"
    VIRTUAL     = "virtual"