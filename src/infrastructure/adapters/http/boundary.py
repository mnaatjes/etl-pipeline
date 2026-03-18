# src/infrastructure/adapters/http/boundary.py
from src.app.ports.input.resource_boundaries import NetworkResourceBoundary
from src.app.domain.models.resource_identity import NetworkAddress, NetworkCoordinate

class HttpResourceBoundary(NetworkResourceBoundary):
    """
    HTTP/HTTPS Resource Boundary.
    Inherits the robust URL-based resolution and safety logic 
    from the NetworkResourceBoundary Port.
    """
    pass
