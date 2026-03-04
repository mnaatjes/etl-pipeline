# src/app/domain/models/packet/completeness.py
from enum import StrEnum

# Define Completeness for Buffering
class Completeness(StrEnum):
    PARTIAL = "partial"
    COMPLETE = "complete"
    BULK = "bulk"