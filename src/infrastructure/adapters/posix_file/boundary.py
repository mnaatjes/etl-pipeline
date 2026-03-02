# src/infrastructure/adapters/posix_file/boundary.py

from pathlib import Path
from src.app.ports.input.resource_boundary import ResourceBoundary
from src.app.domain.models.types import LogicalURI, ValidatedPath

class PosixResourceBoundary(ResourceBoundary[Path]):
    def resolve(self, uri: LogicalURI, anchor: Path) -> Path:
        # 1. Standardixe the anchor
        anchor_absolute = anchor.resolve()

        # 2. Extract sub-path
        # - e.g. registry://key/sub/path.xml --> /sub/path.xml
        # - split by first '/'
        parts = str(uri).split("://")[-1].split("/", 1)
        sub_path = parts[1] if len(parts) > 1 else ""

        # 3. Resolve candidate
        candidate = (anchor_absolute / sub_path).resolve()

        # 4. Security Check
        if not self.is_safe(candidate, anchor_absolute):
            raise PermissionError(f"Boundary Violation! {candidate} escaped {anchor_absolute}")

        # Return Path Object
        return candidate

    def is_safe(self, physical_resource: Path, anchor: Path) -> bool:
        try:
            physical_resource.relative_to(anchor)
            return True
        except ValueError:
            return False