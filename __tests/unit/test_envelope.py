# tests/unit/test_envelope.py
import pytest
from typing import Any
from src.app.ports import envelope
from src.app.ports.envelope import Envelope, RegimeType, Completeness

def test_env_init():
    # Verify standard creation
    payload = b"CMDR Data Chunk"
    env = Envelope(payload=payload)

    assert env.payload == payload
    assert env.regime == RegimeType.BYTES
    assert env.completeness == Completeness.COMPLETE
    assert isinstance(env.metadata, dict)

def test_metadata_isolation():
    envelope_1 = Envelope(payload="first")
    envelope_2 = Envelope(payload="second")

    envelope_1.metadata["id"] = "lorem upsum"
    
    assert "id" in envelope_1.metadata
    assert "id" not in envelope_2.metadata

def test_completeness_assignment():
    env = Envelope(
        payload={"stuff":"cmdr"},
        completeness=Completeness.PARTIAL
    )

    assert env.completeness is Completeness.PARTIAL