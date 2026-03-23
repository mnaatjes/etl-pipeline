from typing import Optional
from src.app.domain.models.resource_identity.base import Address, Coordinate
from src.app.domain.models.resource_identity.types import ResourceKey, Realm

class SyntheticAddress(Address):
    """
    Represents an incoming synthetic (generated) INTENT
    - e.g. 'synthetic://gen/type'
    """
    @property
    def key(self) -> ResourceKey:
        return ResourceKey(self.parsed.authority)

    @property
    def realm(self) -> Realm:
        return Realm.SYNTHETIC

class SyntheticCoordinate(Coordinate):
    """
    Represents the verified generator REALITY
    """
    def __init__(self, generator_id: str, key: Optional[ResourceKey] = None) -> None:
        super().__init__(key)
        self._generator_id = generator_id

    @property
    def realm(self) -> Realm:
        return Realm.SYNTHETIC

    @property
    def protocol(self) -> str:
        return "synthetic"

    @property
    def raw_value(self) -> str:
        return self._generator_id
