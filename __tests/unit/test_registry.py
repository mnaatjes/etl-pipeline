import pytest
from unittest.mock import MagicMock
from src.infrastructure.registry import StreamRegistry
from src.app import DataStream, BasePolicy

# --- MOCK OBJECTS FOR TESTING ---

class MockPolicy(BasePolicy):
    def resolve(self, logical_uri: str):
        # Simply prepends 'resolved/' to prove the registry called it
        return f"resolved/{logical_uri.replace('mock://', '')}"
    
    def list_anchors(self): return []

class MockStream(DataStream):
    def open(self): pass
    def read(self): yield from []
    def write(self, envelope): pass
    def close(self): pass
    def exists(self): return True

# --- TESTS ---

@pytest.fixture
def registry():
    return StreamRegistry(chunk_size=512)

def test_registry_registration(registry):
    """Verifies that we can register a protocol and it's stored correctly."""
    policy = MockPolicy()
    registry.register("mock", MockStream, policy)
    
    assert "mock" in registry._protocols
    assert registry._protocols["mock"].adapter_cls == MockStream
    assert registry._protocols["mock"].policy == policy

def test_registry_get_stream_with_policy(registry):
    """Verifies that the factory injects the policy and resolves the URI."""
    policy = MockPolicy()
    registry.register("mock", MockStream, policy)
    
    # Act
    uri = "mock://path/to/data"
    stream = registry.get_stream(uri, as_sink=True)
    
    # Assert
    assert isinstance(stream, MockStream)
    # The registry should have called policy.resolve()
    assert stream._resource_conf == "resolved/path/to/data"
    assert stream._as_sink is True
    assert stream._chunk_size == 512

def test_registry_get_stream_no_policy(registry):
    """Verifies that the factory works even if no policy is provided."""
    registry.register("open", MockStream, policy=None)
    
    uri = "open://unprotected/data"
    stream = registry.get_stream(uri)
    
    # Should pass the URI raw since there is no policy to resolve it
    assert stream._resource_conf == "open://unprotected/data"
    assert hasattr(stream, '_policy') is False or stream._policy is None

def test_registry_unsupported_protocol(registry):
    """Verifies that an unregistered protocol raises a ValueError."""
    with pytest.raises(ValueError) as excinfo:
        registry.get_stream("unknown://data")
    
    assert "protocol has not been registed" in str(excinfo.value)

def test_registry_passing_use_lines(registry):
    """Verifies that the use_lines flag is correctly passed to the stream."""
    registry.register("file", MockStream)
    
    stream = registry.get_stream("file://test.log", use_lines=True)
    assert stream._use_lines is True