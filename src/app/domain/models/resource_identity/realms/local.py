from typing import Optional
from src.app.domain.models.resource_identity.base import Address, Coordinate
from src.app.domain.models.resource_identity.types import ResourceKey, Realm

class LocalAddress(Address):
    """
    Represents an incoming logical INTENT
    - e.g. 'posix://some-auth/path/to/data'
    """
    @property
    def key(self) -> ResourceKey:
        """e.g. 'posix://scans/file.csv' --> 'scans'"""
        return ResourceKey(self.parsed.authority)
    
    @property
    def realm(self) -> Realm:
        return Realm.LOCAL
    
class LocalCoordinate(Coordinate):
    """
    Represents the verified physical filesystem REALITY
    """
    def __init__(self, path: str, protocol: str = "posix", key: Optional[ResourceKey] = None) -> None:
        super().__init__(key)
        self._path = path
        self._protocol = protocol
    
    @property
    def realm(self) -> Realm:
        return Realm.LOCAL

    @property
    def protocol(self) -> str:
        """Overridden to return the protocol metadata instead of parsing the path."""
        return self._protocol
    
    @property
    def raw_value(self) -> str:
        """Returns the physical path on disk."""
        return self._path
