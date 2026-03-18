from typing import Optional
from src.app.domain.models.resource_identity.base import Address, Coordinate
from src.app.domain.models.resource_identity.types import ResourceKey, Realm

class LocalAddress(Address):
    """
    Represents an incoming logical INTENT
    - e.g. 'posix://some-auth/path/to/data'
    """
    def __init__(self, uri:str) -> None:
        super().__init__(None)
        self._uri = uri

    @property
    def key(self) -> ResourceKey:
        """e.g. 'posix://scans/file.csv' --> 'scans'"""
        return ResourceKey(self.parsed.authority)
    
    @property
    def realm(self) -> Realm:
        return Realm.LOCAL
    
    @property
    def raw_value(self) -> str:
        return self._uri
    
class LocalCoordinate(Coordinate):
    """
    Represents the verified physical filesystem REALITY
    """
    def __init__(self, path:str, key:Optional[ResourceKey] = None) -> None:
        super().__init__(key)
        self._path = path
    
    @property
    def realm(self) -> Realm:
        return Realm.LOCAL
    
    @property
    def protocol(self) -> str:
        return "posix"
    
    @property
    def raw_value(self) -> str:
        return self._path
