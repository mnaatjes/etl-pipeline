from .base import ResourceIdentity, Address, Coordinate
from .types import ResourceKey, ParsedURI, Realm
from .realms import (
    LocalAddress, LocalCoordinate,
    NetworkAddress, NetworkCoordinate,
    MemoryAddress, MemoryCoordinate,
    SyntheticAddress, SyntheticCoordinate,
    VirtualAddress, VirtualCoordinate
)

__all__ = [
    "ResourceIdentity",
    "Address",
    "Coordinate",
    "ResourceKey",
    "ParsedURI",
    "Realm",
    "LocalAddress",
    "LocalCoordinate",
    "NetworkAddress",
    "NetworkCoordinate",
    "MemoryAddress",
    "MemoryCoordinate",
    "SyntheticAddress",
    "SyntheticCoordinate",
    "VirtualAddress",
    "VirtualCoordinate"
]
