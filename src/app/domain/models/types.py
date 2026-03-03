# src/app/domain/models/types.py
from typing import NewType, Union
from pathlib import Path

"""
LogicalURI:
- Request slip; e.g. registry://scans/file_01.csv
- Untrusted string from the user. 
- Represents an intent to access something.
"""
LogicalURI = NewType("LogicalURI", str) 

"""
ResourceKey:
- Nickname / Alias used to look-up anchor paths
- Extracted from the URI
- e.g. "scans"
"""
ResourceKey = NewType("ResourceKey", str)

# 3. REMOTE: A validated external location (HTTP, S3, FTP)
# We use str as the base, but the name 'RemoteURL' provides semantic intent.
RemoteURL = NewType("RemoteURL", str)

# 4. LOCAL: A path that has PASSED through a Sandbox/Boundary.
# The Adapter ONLY accepts this type for POSIX operations.
ValidatedPath = NewType("ValidatedPath", Path)

# 5. THE UNION: The universal type for the DataStream Port.
# This is what the parent DataStream class will now expect.
StreamLocation = Union[RemoteURL, ValidatedPath]