# src/infrastructure/adapters/file/contract.py
from pathlib import Path
from dataclasses import dataclass
from typing import Literal
from src.infrastructure.adapters.posix_file.enums import FileReadMode
from src.app.ports.output.stream_contract import StreamContract

@dataclass(frozen=True)
class PosixFileContract(StreamContract):
    """
    Contract for Local File System Streams.
    Ensures absolute alignment between Python logic and Linux kernel expectations.
    """
    # --- Parent Properties ---
    chunk_size:int = 1024
    use_lines:bool = False
    # --- File Properties ---
    read_mode: FileReadMode = FileReadMode.BYTES
    file_mode: Literal["r", "rb", "w", "wb", "a", "ab", "x", "xb"] = "rb"
    encoding: str = "utf-8"
    permissions: int = 0o664  # Write files (cannot enter directories)

    def __post_init__(self):
        # 1. Universal Type Guard (checks chunk_size, etc.)
        super().__post_init__()

        # 2. Enforce Allowed Range (Synchronized with Type Hint)
        allowed_modes = {"r", "rb", "w", "wb", "a", "ab", "x", "xb"}
        if self.file_mode not in allowed_modes:
            raise ValueError(
                f"Invalid file_mode: '{self.file_mode}'! Must be: {allowed_modes}"
            )
        
        # 3. Binary vs. Text Consistency
        if "b" in self.file_mode:
            if self.read_mode != FileReadMode.BYTES:
                # TODO: Log and Warn
                # Force BYTES to prevent UnicodeDecodeErrors in the adapter
                print(f"[WARNING] read_mode set to BYTES")
                object.__setattr__(self, "read_mode", FileReadMode.BYTES)

        # 4. Sink (Write) Logic: Nullify Read Strategy
        write_modes = {"w", "wb", "a", "ab", "x", "xb"}
        if self.file_mode in write_modes:
            # TODO: Log and Warn
            print(f"[Warning] read_mode set to NONE")
            object.__setattr__(self, "read_mode", FileReadMode.NONE)

        # 5. Octal Range Enforcement (0o000 - 0o777)
        if not (0 <= self.permissions <= 0o777):
            raise ValueError(
                f"Invalid Permissions: {oct(self.permissions)} ({self.permissions} decimal). "
                f"Must be between 0o000 and 0o777. Check for missing '0o' prefix."
            )

        # 6. Security Audit: Check for 'World Writable'
        if self.file_mode in write_modes and (self.permissions & 0o002):
            print(f"[SECURITY WARNING] Creating/Writing to '{self.file_mode}' "
                  f"with world-writable bits ({oct(self.permissions)}) is dangerous!")