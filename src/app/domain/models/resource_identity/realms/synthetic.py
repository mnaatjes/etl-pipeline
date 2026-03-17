from src.app.domain.models.resource_identity.base import Address, Coordinate
from src.app.domain.models.resource_identity.types import ResourceKey, Realm

class SyntheticAddress(Address):
    """
    Represents an incoming synthetic (generated) INTENT
    - e.g. 'synthetic://gen/type'
    """
    def __init__(self, uri: str) -> None:
        self._uri = uri

    @property
    def key(self) -> ResourceKey:
        return ResourceKey(self.parsed.authority)

    @property
    def realm(self) -> Realm:
        return Realm.SYNTHETIC

    @property
    def raw_value(self) -> str:
        return self._uri

class SyntheticCoordinate(Coordinate):
    """
    Represents the verified generator REALITY
    """
    def __init__(self, generator_id: str, key: ResourceKey) -> None:
        self._generator_id = generator_id
        self._key = key

    @property
    def key(self) -> ResourceKey:
        return self._key

    @property
    def realm(self) -> Realm:
        return Realm.SYNTHETIC

    @property
    def protocol(self) -> str:
        return "synthetic"

    @property
    def raw_value(self) -> str:
        return self._generator_id
