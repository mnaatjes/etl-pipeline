from src.app.domain.models.resource_identity.base import Address, Coordinate
from src.app.domain.models.resource_identity.types import ResourceKey, Realm

class VirtualAddress(Address):
    """
    Represents an incoming logical virtual INTENT
    - e.g. 'virtual://registry/item'
    """
    def __init__(self, uri: str) -> None:
        self._uri = uri

    @property
    def key(self) -> ResourceKey:
        return ResourceKey(self.parsed.authority)

    @property
    def realm(self) -> Realm:
        return Realm.VIRTUAL

    @property
    def raw_value(self) -> str:
        return self._uri

class VirtualCoordinate(Coordinate):
    """
    Represents the verified virtual REALITY
    """
    def __init__(self, virtual_path: str, key: ResourceKey) -> None:
        self._virtual_path = virtual_path
        self._key = key

    @property
    def key(self) -> ResourceKey:
        return self._key

    @property
    def realm(self) -> Realm:
        return Realm.VIRTUAL

    @property
    def protocol(self) -> str:
        return "virtual"

    @property
    def raw_value(self) -> str:
        return self._virtual_path
