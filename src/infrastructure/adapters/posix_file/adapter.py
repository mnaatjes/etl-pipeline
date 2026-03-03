# src/infrastructure/adapters/posix_file/adapter.py

import os
from typing import Type, Iterator, Optional, IO
from pathlib import Path
from src.app.ports.output.datastream import DataStream
from src.app.domain.models.envelope import Envelope
from src.app.domain.models.resource_identity import PhysicalPath
from src.infrastructure.adapters.posix_file.contract import PosixFileContract
from src.infrastructure.adapters.posix_file.policy import PosixFilePolicy
from src.infrastructure.adapters.posix_file.enums import FileReadMode

class PosixFileStream(DataStream[PosixFileContract]):
    """
    Adapter for POSIX - Linux - file I/O

    """
    def __init__(self, uri:PhysicalPath, policy:PosixFilePolicy, as_sink: bool|None = False, **settings) -> None:
        """Parent DataStream Parameter Pass"""
        super().__init__(uri, as_sink, policy, **settings)
        # PhysicalPath type for Resource Boundary Catalog / Path() object
        # REAL Type Check: Ensures we aren't dealing with a string
        if not isinstance(uri, Path):
            # We provide a detailed error so the developer knows they missed the Catalog step
            raise TypeError(
                f"PosixFileStream integrity violation. Expected Path (PhysicalPath), "
                f"but received {type(uri)}. Did you forget to call resource_catalog.resolve_uri()?"
            )
        self._path: Path = uri

        # Physical Connection between Python and Linux Filesystem
        # - Stores io.TextIOWrapper or io.BufferedRandom object
        self._file_handle: Optional[IO] = None
        
        # 2. Re-assert the type for the specific child class
        # This resolves the "Unknown Attribute" error in the methods below.
        self._policy: PosixFilePolicy = policy or PosixFilePolicy()

    @property
    def _settings_contract(self) -> Type[PosixFileContract]:
        return PosixFileContract

    def exists(self) -> bool:
        """Standard POSIX check via pathlib."""
        return self._path.exists()
    
    def open(self) -> None:
        """
        Connects Python to the Linux Filesystem.
        Handles directory creation for sinks and encoding for text modes.
        """
        # 1. Safety check for writers
        if self._as_sink:
            self._ensure_directory_exists()

        # 2. Extract settings from the Contract
        # Binary modes (rb, wb) MUST NOT have an encoding passed to open()
        is_binary = "b" in self._settings.file_mode
        encoding = None if is_binary else self._settings.encoding

        # 3. Perform the actual OS open
        try:
            self._file_handle = open(
                self._path, 
                mode=self._settings.file_mode, 
                encoding=encoding
            )
            self.is_open = True
        except (FileNotFoundError, PermissionError) as e:
            # We wrap OS errors in a domain-friendly IOError
            raise IOError(f"Could not open {self._path}: {e}")

    def read(self) -> Iterator[Envelope]:
        """
        Dispatches reading based on the Contract strategy.
        Yields Envelopes to the StreamManager.
        """
        if not self._file_handle or self._file_handle.closed:
            raise IOError("Attempted to read from a closed stream.")

        strategy = self._settings.read_mode

        if strategy == FileReadMode.BYTES:
            while chunk := self._file_handle.read(self.chunk_size):
                yield Envelope(payload=chunk)
        
        elif strategy == FileReadMode.LINES:
            for line in self._file_handle:
                yield Envelope(payload=line)
                
        elif strategy == FileReadMode.TEXT:
            while chunk := self._file_handle.read(self.chunk_size):
                yield Envelope(payload=chunk)

    def write(self, envelope: Envelope) -> None:
        """
        Writes the envelope payload to disk.
        Forces permission sync (os.chmod) on every write to ensure Linux compliance.
        """
        if not self._file_handle or self._file_handle.closed:
            raise IOError("Attempted to write to a closed stream.")

        self._file_handle.write(envelope.payload)
        
        # Ensure file permissions match the contract (e.g. 0o664)
        if self._as_sink:
            os.chmod(self._path, self._settings.permissions)

    def close(self) -> None:
        if self._file_handle:
            self._file_handle.close()
            self._file_handle = None

    # --- Helper Methods ---

    def _ensure_directory_exists(self) -> None:
        """Creates the parent structure if missing, applying Policy-governed permissions."""
        parent = self._path.parent
        if not parent.exists():
            # Calculate 0o775 from 0o644 policy to write and enter directories
            dir_perms = self._policy.derive_dir_permissions(file_perms=self._settings.permissions)

            # Make Dir Path
            parent.mkdir(parents=True, exist_ok=True, mode=dir_perms)