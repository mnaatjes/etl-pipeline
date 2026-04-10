# LocalFilePolicy Resolution Strategy

In a production-grade Linux data pipeline, a resolve() method acts as the "Physical-to-Logical Mapping Layer." It is the bridge between your high-level application code and the messy, permissioned reality of the filesystem.

Here is what the "ideal" logic of a resolve() method should be based on industry best practices.

## 1. What it SHOULD contain

A professional resolve() method should follow a Priority-Based Waterfall strategy:

*   **Idempotency (Self-Recognition):** If you pass it a path it has already resolved, it should recognize it and return it immediately without trying to "re-re-resolve" it.
*   **Logical-to-Physical Translation:** It should map "Human-Friendly" keys (like journal) to "OS-Friendly" paths (like /mnt/ssd/data/elite/journals).
*   **Security Sandboxing (Chroot-lite):** It must verify that the final path is a child of an authorized "Anchor." If the math results in a path outside the sandbox, it should blow up.
*   **Normalization:** It should handle OS-specific quirks, such as stripping file:// prefixes or collapsing redundant separators (e.g., data//logs → data/logs).

## 2. What it SHOULD do

The logic should follow these three distinct phases:

| Phase | Action | Purpose |
| :--- | :--- | :--- |
| **Normalize** | Clean input strings and convert to Path objects. | Removes user input noise (extra slashes, protocols). |
| **Identify** | Check if the path is Physical (Absolute) or Logical (Alias). | Decides whether to validate the location or translate the key. |
| **Validate** | Confirm the path exists within a permitted "Anchor." | Prevents Path Traversal attacks (e.g., ../../etc/shadow). |

## 3. What it SHOULD NOT do

This is where most "brittle" designs fail. A clean resolve() method should avoid the following:

*   **Avoid State Dependency:** It should NOT rely on os.getcwd() or Path.cwd(). The logic should work whether you run the code from /srv/pipeline or from your home directory.
*   **Avoid Auto-Creation:** It should NOT create folders (e.g., mkdir). Resolution is a Read-Only mental exercise. The "Worker" (the Stream) should handle the physical creation.
*   **Avoid Implicit Permissions:** It should NOT check if a file is readable or writable. It only tells you where it is; let the OS handle the access denied errors when you actually try to open it.
*   **Avoid "Magic" Hardcoding:** It should never have hardcoded strings like "/tmp" or "/home/user". All physical roots must be provided via the Policy's configuration.

## 4. The "Ideal" Architecture Logic

If we were building this for a high-concurrency Linux environment, the logic would look like this:

1.  **Check Physicality:** Is this a full absolute path?
    *   If yes: Check if it starts with any of my registered Anchor paths. If yes, it's already resolved. Return it.
2.  **Translate Logical:** Is the first segment of the path an Anchor Key?
    *   If yes: Replace the key with the physical path and join the remainder.
3.  **Final Sandbox Check:** Does the resolved path still start with the Anchor's physical path? (Guards against key/../../etc).
4.  **Resolve Links:** Use .resolve() to follow symlinks and get the "Real" absolute path on the disk.

### Why this matters for the ProDesk

In your Elite Dangerous project, this "Best Practice" design means you can move your data between a local tmp folder for testing and a massive SSD for production without changing a single line of your processing code. The resolve() method is your Isolation Layer.

```python
def resolve(self, logical_uri: str) -> Path:
    """
    Translates a logical URI or physical path into a validated absolute Path.
    Priority:
    1. Identification: Is it already a physical path?
    2. Translation: If logical, map the key to a physical anchor.
    3. Validation: Strict boundary check (Chroot-lite).
    """
    # --- 1. Normalization ---
    # Strip protocols and leading slashes to get a clean relative-style string
    clean_path = str(logical_uri).replace("file://", "").lstrip("/")
    input_path = Path(clean_path)
    
    # --- 2. Identity Check (Idempotency) ---
    # If the input is already absolute (e.g. from a previous resolve), 
    # check if it's already safe.
    if Path(logical_uri).is_absolute():
        abs_input = Path(logical_uri)
        for anchor_path in self._anchors.values():
            try:
                abs_input.relative_to(anchor_path)
                return abs_input.resolve() # Already physical and authorized
            except ValueError:
                continue

    # --- 3. Logical Mapping ---
    # Split into [key, sub_path...]
    segments = input_path.parts
    if not segments:
        raise ValueError("Empty path provided to resolve()")
        
    key = segments[0]
    remaining_parts = segments[1:]

    if key not in self._anchors:
        raise PermissionError(
            f"Unauthorized: Key '{key}' is not a registered anchor. "
            f"Available: {self.list_anchors()}"
        )

    anchor = self._anchors[key]

    # --- 4. Deduplication & Construction ---
    # Handle the case where the user repeated the anchor name in the path
    # e.g. 'data/data/logs' -> 'data/logs'
    while remaining_parts and remaining_parts[0] in anchor.parts:
        remaining_parts = remaining_parts[1:]

    # Construct the final physical path
    full_path = anchor.joinpath(*remaining_parts).resolve()

    # --- 5. Security Guard (The Sandbox) ---
    # Ensure the final path hasn't escaped the anchor via '../../'
    try:
        full_path.relative_to(anchor)
    except (ValueError, RuntimeError):
        raise PermissionError(f"PATH TRAVERSAL BLOCKED: {full_path} escapes {anchor}")

    return full_path
```
