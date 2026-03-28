# Issue: Comprehensive CRUD and Metadata for StreamHandle

**Status:** Proposed  
**Priority:** Medium (Developer Experience)  
**Component:** Stream Subsystem (`StreamHandle`)

## 1. Problem Statement
Currently, the `StreamHandle` only implements `read()` and `write()` operations. While these handle the "Data-in-Motion," the handle lacks methods to manage the "Resource-at-Rest" or its metadata. 

Users who have a `StreamHandle` must currently go back to the `Gateway` or `StreamManager` to perform operations like `delete()`, `info()`, or `list()`, which creates friction in the API.

## 2. Proposed Goals
Transform the `StreamHandle` into a complete **Resource Dashboard** by implementing the following operations:

| Method | Role | Implementation Strategy |
| :--- | :--- | :--- |
| **`info()`** | Metadata Discovery | Delegate to `self._adapter.__class__.info(self.uri)`. |
| **`delete()`** | Resource Removal | Ensure handle is closed, then delegate to `adapter.delete(self.uri)`. |
| **`exists()`** | Validation | Delegate to `self._adapter.__class__.exists(self.uri)`. |
| **`list()`** | Content Discovery | (If a directory) Return an iterator of `StreamHandle` objects for children. |
| **`move(dest)`** | Relocation | Coordinate with `StreamManager` to relocate the resource. |

## 3. Architectural Considerations

### A. Instance vs. Class Methods
In the `DataStream` port, discovery methods like `info()` and `list()` are `@classmethods` because they don't require an open stream.
*   **The Handle Advantage:** Since the `StreamHandle` already knows its `uri` and its `adapter` class, it can call these methods cleanly without the user needing to provide any arguments.

### B. The "Recursive Browser" Pattern
If `handle.list()` is implemented, it should return an iterator of **`StreamHandle`** objects rather than raw `Coordinate` objects.
*   **Why?** This allows for "Fluent Browsing":
    ```python
    # Example of the 'Browser' Pattern
    directory = app.get_handle("posix://data")
    for file_handle in directory.list():
        if file_handle.info()['size'] > 1024:
            file_handle.delete()
    ```

### C. Close-Before-Delete Safety
The `StreamHandle` must enforce safety. A resource should not be deleted if the stream is currently `is_open`. The `delete()` method in the handle should automatically handle the `close()` sequence or raise an error if the stream is active.

## 4. Proposed User Flow
```python
handle = app.get_handle("posix://data/report.pdf")

# Inspecting metadata without leaving the handle context
metadata = handle.info()
print(f"Size: {metadata['size']} bytes")

# Deleting the resource directly from the dashboard
if metadata['size'] == 0:
    handle.delete()
```

## 5. Next Steps
1.  Implement `info()` and `exists()` in `StreamHandle` as simple passthroughs.
2.  Implement `delete()` with "Open State" safety guards.
3.  Refactor `list()` to support the "Recursive Browser" pattern by returning new `StreamHandle` instances.
