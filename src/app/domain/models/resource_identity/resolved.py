# src/app/domain/models/resource_identity/resolved.py

from dataclasses import dataclass
from src.app.domain.models.resource_identity import StreamLocation

@dataclass(frozen=True)
class ResolvedResource:

    location: StreamLocation

