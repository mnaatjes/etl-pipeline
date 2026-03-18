from urllib.parse import urljoin, urlparse
from .base import ResourceBoundary
from src.app.domain.models.resource_identity import NetworkAddress, NetworkCoordinate

class NetworkResourceBoundary(ResourceBoundary):
    """Refined Port for anything in the NETWORK realm (HTTP, S3, FTP)."""

    def resolve(self, address: NetworkAddress, anchor: NetworkCoordinate) -> NetworkCoordinate:
        """
        Standard URL Resolution Logic.
        Enforces authority locking and scheme consistency.
        """
        # 1. AUTHORITY LOCK: If address provides a host, it MUST match anchor
        if address.authority and address.authority != anchor.authority:
             # ALLOW if it's a registry intent (Librarian lookup)
             if address.protocol != "registry":
                  raise PermissionError(f"Boundary Violation: Authority mismatch: {address.authority} != {anchor.authority}")

        # 2. SCHEME CONSISTENCY
        if address.protocol and address.protocol != "registry" and address.protocol != anchor.protocol:
            raise PermissionError(f"Protocol Mismatch: Cannot resolve {address.protocol} against {anchor.protocol} anchor")

        # 3. RESOLUTION
        base_url = anchor.raw_value
        
        # OPTIMIZATION: If the address is already a full URL matching the anchor, 
        # we don't need to join it (prevents v1/v1 issues)
        if address.protocol != "registry" and address.raw_value.startswith(base_url):
             resolved_url = address.raw_value
        else:
            if not base_url.endswith("/"): base_url += "/"
            # We strip leading slash to ensure urljoin treats it as relative to the base_url
            sub_path = address.parsed.path.lstrip("/")
            # Standard URL Joining
            resolved_url = urljoin(base_url, sub_path)

        # 4. FINAL VERIFY: Did the host or protocol change during resolution?
        resolved_parsed = urlparse(resolved_url)
        base_parsed = urlparse(base_url)
        
        if resolved_parsed.netloc != base_parsed.netloc:
            raise PermissionError(f"Boundary Violation: Host redirection detected to {resolved_parsed.netloc}")
            
        if resolved_parsed.scheme != base_parsed.scheme:
             raise PermissionError(f"Boundary Violation: Protocol redirection detected to {resolved_parsed.scheme}")

        return NetworkCoordinate(url=resolved_url, key=address.key)

    def is_safe(self, resource: NetworkCoordinate, anchor: NetworkCoordinate) -> bool:
        """Universal Network Safety: Prefix matching."""
        return resource.raw_value.startswith(anchor.raw_value)
