# src/app/domain/models/resource_identity/physical_uri.py
from src.app.domain.models.resource_identity.base import ResourceIdentity
from src.app.domain.models.resource_identity.types import ResourceKey

class PhysicalURI(str, ResourceIdentity):
    """
    A direct-access coordinate (https://, s3://).
    Inherits from str for compatibility with network clients.
    """
    def __new__(cls, value: str):
        if "://" not in value:
            raise ValueError(f"PhysicalURI requires a scheme. Got: {value}")
        return super().__new__(cls, value)

    @property
    def key(self) -> ResourceKey:
        # For physical URIs, the 'key' is often the domain or bucket
        return ResourceKey(self.split("://")[1].split("/")[0])

    @property
    def protocol(self) -> str:
        return self.split("://")[0]