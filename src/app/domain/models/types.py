# src/app/domain/models/types.py
from typing import NewType
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

"""
ValidatedPath:
- A Trusted Object
- Represents a path that has been proven and is_safe
"""
# 3. A path that has PASSED through a Sandbox/Boundary
# The Adapter ONLY accepts this type.
ValidatedPath = NewType("ValidatedPath", Path)