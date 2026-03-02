# src/app/domain/models/types.py
from typing import NewType
from pathlib import Path

# 1. Untrusted input from the outside world
LogicalURI = NewType("LogicalURI", str) 

# 2. A Key extracted from a URI (e.g., 'scans' from 'local://scans/...')
ResourceKey = NewType("ResourceKey", str)

# 3. A path that has PASSED through a Sandbox/Boundary
# The Adapter ONLY accepts this type.
ValidatedPath = NewType("ValidatedPath", Path)