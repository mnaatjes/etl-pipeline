# src/app/domain/models/resource_identity/logical_uri.py
from src.app.domain.models.resource_identity.base import ResourceIdentity
from src.app.domain.models.resource_identity.types import ResourceKey

class LogicalURI(str, ResourceIdentity):
    """The 'registry://' alias used for internal governing."""
    def __new__(cls, value: str):
        if not value.startswith("registry://"):
            raise ValueError("LogicalURI must use 'registry://' protocol.")
        return super().__new__(cls, value)

    @property
    def key(self) -> ResourceKey:
        # registry://scans/file.csv -> scans
        return ResourceKey(self.replace("registry://", "").split("/")[0])