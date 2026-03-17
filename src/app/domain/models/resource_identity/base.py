# src/app/domain/models/resource_identity.py/base.py
from abc import ABC, abstractmethod
from functools import cached_property
from src.app.domain.models.resource_identity.types import ResourceKey, ParsedURI, Realm

# --- PARENT: Resource Identity ---

class ResourceIdentity(ABC):

    # --- Abstract Properties: IDENTITY ---

    @property
    @abstractmethod
    def key(self) -> ResourceKey:
        """The logical identifier used for cataloging and logging."""
        pass

    @property
    @abstractmethod
    def realm(self) -> Realm:
        """The logical realm: local, network, memory, synthetic, virtual"""
        pass

    @property
    @abstractmethod
    def raw_value(self) -> str:
        """The Primitive representation of the URI, Path, etc"""
        pass

    @cached_property
    def parsed(self) -> ParsedURI:
        """Decomposes raw_value into URI parts"""
        return ParsedURI.from_string(self.raw_value)

    # --- Concrete Properties ---
    
    @property
    def protocol(self) -> str:
        """The scheme of or type: e.g. posix, http, registry..."""
        return self.parsed.protocol

    @property
    def authority(self) -> str:
        """
        Part of URI that follows protocol scheme '://' 
        - e.g. s3://bucket/path... authority == 'bucket'
        """
        return self.parsed.authority

    @property
    def is_local(self) -> bool: return self.realm == Realm.LOCAL

    @property
    def is_remote(self) -> bool: return self.realm == Realm.NETWORK

    @property
    def is_synthetic(self) -> bool: 
        """Is this data procedurally genorated i.e. not stored?"""
        return self.realm == Realm.SYNTHETIC

    @property
    def is_memory(self) -> bool: 
        """Is this data stored in-process i.e. RAM?"""
        return self.realm == Realm.MEMORY

    @property
    def is_address(self) -> bool:
        """Does this identity represent a reference that needs a resolution?"""
        return False
    
    @property
    def is_coordinate(self) -> bool:
        """Does this identity represent a physical reality ready for I/O?"""
        return False
    
    # --- Methods ---

    def __str__(self) -> str:
        """Returns the canonical string representation, i.e. the URI"""
        return str(self.raw_value)
    
# --- CHILD: Address (fmr: Resource Identifier) ---

class Address(ResourceIdentity):
    """
    Represents an incoming 'INTENT'
    - a URI string
    - Must be Resolvable
    """
    @property
    def is_address(self) -> bool: return True

# --- CHILD: Coordinate (fmr: Stream Location) ---
class Coordinate(ResourceIdentity):
    """
    Represents a 'PHYSICAL REALITY'
    - Must provide a protocol string
    - The data is physically here, i.e. /src/data/path/to/file.txt
    """
    @property
    def is_coordinate(self) -> bool: return True