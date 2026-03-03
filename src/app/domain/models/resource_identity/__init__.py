# src/app/domain/models/resource_identity/__init__.py
from typing import Union

# 1. Import the Type Primitives
from .types import ResourceKey

# 2. Import the Identifier Implementations (The "Addresses")
from .logical_uri import LogicalURI
from .physical_uri import PhysicalURI
from .remote_url import RemoteURL

# 3. Import the Location Implementations (The "Physical Realities")
from .physical_path import PhysicalPath  # Assuming class name is ValidatedPath inside

# --- THE UMBRELLA UNIONS ---

"""
ResourceIdentifier:
The global category for all incoming resource strings once promoted to Value Objects.
Encompasses both the 'Nickname' (Logical) and the 'Coordinate' (Physical).
"""
ResourceIdentifier = Union[LogicalURI, PhysicalURI]

"""
StreamLocation:
The final, resolved state of a resource identity. 
This is what the StreamManager uses to pick an Adapter.
"""
StreamLocation = Union[PhysicalPath, PhysicalURI]

# --- PUBLIC API ---

__all__ = [
    "ResourceKey",
    "LogicalURI",
    "PhysicalURI",
    "RemoteURL",
    "PhysicalPath",
    "ResourceIdentifier",
    "StreamLocation",
]