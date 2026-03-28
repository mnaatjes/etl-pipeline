from typing import Optional
from src.app.domain.models.resource_identity.base import Address, Coordinate
from src.app.domain.models.resource_identity.types import ResourceKey, Realm

class NetworkAddress(Address):
    """
    Represents an incoming network INTENT
    - e.g. 'https://api.example.com/data'
    """
    @property
    def key(self) -> ResourceKey:
        return ResourceKey(self.parsed.authority)

    @property
    def realm(self) -> Realm:
        return Realm.NETWORK

class NetworkCoordinate(Coordinate):
    """
    Represents the verified network REALITY (URL)
    """
    def __init__(self, url: str, protocol:str = "https", key: Optional[ResourceKey] = None) -> None:
        super().__init__(key)
        self._url = url
        self._protocol = protocol

    @property
    def realm(self) -> Realm:
        return Realm.NETWORK

    @property
    def raw_value(self) -> str:
        return self._url
