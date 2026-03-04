# Domain-Specific Wrappers (DSW)

## 1. Definition
A Domain-Specific Wrapper is a high-level abstraction layer that sits between the application's business logic and the generic `StreamFlow` framework. It translates "Business Language" (e.g., "Save Scan", "Get Patient Record") into "Framework Language" (e.g., "Write to registry://scans/...", "Read from posix://records/...").

## 2. Architectural Positioning
The DSW serves as a **Domain Service** or a **Repository** depending on its complexity.

```text
[ Business Logic ]
       |
       v
[ Domain-Specific Wrapper ]  <-- (ScanStorageClient, DataWarehouse)
       |
       v
[ StreamClient (Facade) ]    <-- (The Framework Entry Point)
       |
       v
[ StreamManager (Engine) ]
```

## 3. Implementation Example

```python
from src.app.stream_client import StreamClient
from pathlib import Path

class ScanStorageClient:
    """
    A DSW for handling high-resolution medical scans.
    Hides all URI construction and protocol details from the app.
    """
    def __init__(self, stream_client: StreamClient, root_dir: str):
        self._client = stream_client
        # Configuration is encapsulated here
        self._client.add_resource(
            key="scans", 
            protocol="posix", 
            anchor=Path(root_dir)
        )

    def save_scan(self, scan_id: str, data: bytes):
        """High-level intent: 'Save this scan'."""
        # The logic for naming and storage location is central here
        uri = f"posix://scans/{scan_id}.raw"
        self._client.write(uri, data)

    def get_physical_path(self, scan_id: str) -> Path:
        """High-level intent: 'Where is this file on disk?'."""
        return self._client.resolve(f"posix://scans/{scan_id}.raw")
```

## 4. Why use a DSW?
1. **Decoupling:** If the storage moves from local disk to S3, you only change the DSW configuration, not the business logic.
2. **Type Safety:** You can return specialized Domain Objects instead of raw bytes.
3. **DRY (Don't Repeat Yourself):** All URI formatting logic (e.g., `f"posix://scans/{id}.raw"`) exists in exactly one place.
