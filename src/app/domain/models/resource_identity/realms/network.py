from src.app.domain.models.resource_identity.base import Address, Coordinate
from src.app.domain.models.resource_identity.types import ResourceKey, Realm

class NetworkAddress(Address):
    """
    Represents an incoming network INTENT
    - e.g. 'https://api.example.com/data'
    """
    def __init__(self, uri: str) -> None:
        self._uri = uri

    @property
    def key(self) -> ResourceKey:
        return ResourceKey(self.parsed.authority)

    @property
    def realm(self) -> Realm:
        return Realm.NETWORK

    @property
    def raw_value(self) -> str:
        return self._uri

class NetworkCoordinate(Coordinate):
    """
    Represents the verified network REALITY (URL)
    """
    def __init__(self, url: str, key: ResourceKey) -> None:
        self._url = url
        self._key = key

    @property
    def key(self) -> ResourceKey:
        return self._key

    @property
    def realm(self) -> Realm:
        return Realm.NETWORK

    @property
    def raw_value(self) -> str:
        return self._url
