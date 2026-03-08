# src/infrastructure/adapters/posix_file/adapter.py
import os
from typing import Type, Iterator, Optional, IO
from pathlib import Path
from src.app.ports.output.datastream import DataStream
from src.app.domain.models.streams import StreamCapacity, StreamContext
from src.app.domain.models.packet import Packet, FlowSignal, PayloadSubject, Completeness
from src.app.domain.models.resource_identity import PhysicalPath, StreamLocation
from src.infrastructure.adapters.posix_file.contract import PosixFileContract
from src.infrastructure.adapters.posix_file.policy import PosixFilePolicy
from src.infrastructure.adapters.posix_file.enums import FileReadMode

class PosixFileStream(DataStream[PosixFileContract]):
    """
    Adapter for POSIX - Linux - file I/O

    """
    def __init__(
            self, 
            uri: StreamLocation,
            context: StreamContext,
            policy: PosixFilePolicy, 
            as_sink: bool = False, 
            **settings
    ) -> None:
        """Parent DataStream Parameter Pass"""
        from src.app.domain.models.resource_identity import PhysicalURI

        # If writing, default to 'wb' if no mode provided
        if as_sink and "file_mode" not in settings:
            settings["file_mode"] = "wb"

        # 1. Coordinate Conversion (PhysicalURI -> Path)
        if isinstance(uri, PhysicalURI):
            if uri.protocol != "file":
                raise TypeError(f"PosixFileStream cannot handle non-file URI: {uri.protocol}")
            # Extract path from file:///...
            self._path = Path(uri.split("://")[1])
        elif isinstance(uri, Path):
            self._path = uri
        else:
            raise TypeError(
                f"PosixFileStream integrity violation. Expected Path or PhysicalURI, "
                f"but received {type(uri)}."
            )

        super().__init__(uri, context, as_sink, policy, **settings)

        # Physical Connection between Python and Linux Filesystem
        # - Stores io.TextIOWrapper or io.BufferedRandom object
        self._file_handle: Optional[IO] = None

        # 2. Re-assert the type for the specific child class
        # This resolves the "Unknown Attribute" error in the methods below.
        self._policy: PosixFilePolicy = policy or PosixFilePolicy()

    # --- PROPERTIES ---

    @property
    def capacity(self) -> StreamCapacity:
        return StreamCapacity(
            can_seek=True,
            is_readable=True,
            is_writable=True,
            supports_append=True,
            is_network=False
        )

    @property
    def _settings_contract(self) -> Type[PosixFileContract]:
        return PosixFileContract

    @classmethod
    def exists(cls, location: StreamLocation) -> bool:
        """
        High-Resolution Existence Check.
        
        Uses the Class-level expert logic to verify the physical coordinate 
        before the stream machinery is even initialized.
        """
        # 1. Type Guard: Ensure we aren't trying to check a URL with a File Scout
        if not isinstance(location, PhysicalPath):
            # If the factory somehow handed an S3/HTTP URI to the Posix adapter,
            # we return False as this adapter cannot verify that medium.
            return False

        # 2. Execution: PhysicalPath inherits from pathlib.Path
        # No need for manual 'os.path.exists'—the type handles its own reality.
        return location.exists()
    
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

    def read(self) -> Iterator[Packet]:
        """
        Dispatches reading based on the Contract strategy.
        Yields Packets to the StreamManager.
        """
        if not self._file_handle or self._file_handle.closed:
            raise IOError("Attempted to read from a closed stream.")

        strategy = self._settings.read_mode

        if strategy == FileReadMode.BYTES:
            while chunk := self._file_handle.read(self.chunk_size):
                yield Packet(
                    payload=chunk,
                    context=self._context,
                    subject=PayloadSubject.BYTES,
                    signal=FlowSignal.STREAM_DATA,
                    completeness=Completeness.PARTIAL
                )
        
        elif strategy == FileReadMode.LINES:
            for line in self._file_handle:
                yield Packet(
                    payload=line,
                    context=self._context,
                    subject=PayloadSubject.BYTES,
                    signal=FlowSignal.STREAM_DATA,
                    completeness=Completeness.COMPLETE
                )
                
        elif strategy == FileReadMode.TEXT:
            while chunk := self._file_handle.read(self.chunk_size):
                yield Packet(
                    payload=chunk,
                    context=self._context,
                    subject=PayloadSubject.BYTES,
                    signal=FlowSignal.STREAM_DATA,
                    completeness=Completeness.PARTIAL
                )

    def write(self, packet: Packet) -> None:
        """
        Writes the packet payload to disk.
        Forces permission sync (os.chmod) on every write to ensure Linux compliance.
        """
        if not self._file_handle or self._file_handle.closed:
            raise IOError("Attempted to write to a closed stream.")

        self._file_handle.write(packet.payload)
        
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