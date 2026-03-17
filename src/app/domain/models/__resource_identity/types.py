from typing import NewType

"""
ResourceKey:
- Nickname / Alias used to look-up anchor paths
- Extracted from the URI
- e.g. "scans"
"""
ResourceKey = NewType("ResourceKey", str)