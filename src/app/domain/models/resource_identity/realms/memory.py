from src.app.domain.models.resource_identity.base import Address, Coordinate
from src.app.domain.models.resource_identity.types import ResourceKey, Realm

class MemoryAddress(Address):
    """
    Represents an incoming memory-based INTENT
    - e.g. 'memory://cache/key'
    """
    def __init__(self, uri: str) -> None:
        self._uri = uri

    @property
    def key(self) -> ResourceKey:
        return ResourceKey(self.parsed.authority)

    @property
    def realm(self) -> Realm:
        return Realm.MEMORY

    @property
    def raw_value(self) -> str:
        return self._uri

class MemoryCoordinate(Coordinate):
    """
    Represents the verified in-process memory REALITY
    """
    def __init__(self, reference: str, key: ResourceKey) -> None:
        self._reference = reference
        self._key = key

    @property
    def key(self) -> ResourceKey:
        return self._key

    @property
    def realm(self) -> Realm:
        return Realm.MEMORY

    @property
    def protocol(self) -> str:
        return "memory"

    @property
    def raw_value(self) -> str:
        return self._reference
