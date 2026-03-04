# src/app/domain/models/resource_identity/logical_uri.py
from urllib.parse import urlparse
from src.app.domain.models.resource_identity.base import ResourceIdentity
from src.app.domain.models.resource_identity.types import ResourceKey

class LogicalURI(str, ResourceIdentity):
    """
    The 'registry://' alias used for internal governing.
    - Modified to also accept user registered protocols for resolution
    - e.g. add_resource("posix://...") allows for resolve("posix://key")
    - Uses RFC 3986 standards
    """
    def __new__(cls, value: str):
        if "://" not in value:
            # 
            raise ValueError(f"LogicalURI requires a scheme; e.g. '://...' and got: {value}")
        return super().__new__(cls, value)

    @property
    def key(self) -> ResourceKey:
        # registry://scans/file.csv -> scans
        return ResourceKey(urlparse(self).netloc)
    
    @property
    def protocol(self) -> str:
        """Extracts the scheme (e.g. registry, posix, file, https...)"""
        return urlparse(self).scheme
    
    @property
    def path(self) -> str:
        """
        Extracts the remainder of the URI 
        - i.e. sub-path 
        - from 'file://path/to/file' --> to 'to/file/'
        """
        return urlparse(self).path.lstrip("/")