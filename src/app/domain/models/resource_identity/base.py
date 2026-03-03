# src/app/domain/models/resource_identity/base.py
from abc import ABC, abstractmethod
from src.app.domain.models.resource_identity.types import ResourceKey

class ResourceIdentity(ABC):
    """
    The Abstract Base for all data identities in the system.
    Ensures that every resource, resolved or logical, has a Key.
    """
    @property
    @abstractmethod
    def key(self) -> ResourceKey:
        """The logical identifier used for cataloging and logging."""
        pass