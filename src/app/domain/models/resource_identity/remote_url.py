# src/app/domain/models/resource_identity/remote_url.py
from src.app.domain.models.resource_identity.physical_uri import PhysicalURI

class RemoteURL(PhysicalURI):
    """Specific implementation for HTTP/S3 transports."""
    pass