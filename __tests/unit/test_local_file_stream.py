# tests/unit/test_local_file_stream.py
import pytest
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field
from src.infrastructure import LocalFileStream
from src.infrastructure import LocalFilePolicy
from src.app.ports.envelope import Envelope

@pytest.fixture
def policy(tmp_path):
    """Setup a standard test policy with a sandbox in /tmp."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return LocalFilePolicy({"data": str(data_dir)})

@dataclass
class PathTest:
    path: str
    expected_suffix: str  # What we expect the end of the path to look like
    is_valid: bool = True

def test_local_fs_policy(p=False):
    # Setup policy (Note: .resolve() in __init__ makes these absolute to CWD)
    policy = LocalFilePolicy({
        "tmp": "tests/data/tmp",
        "data": "tests/data/",
        "out": "tests/data/downloads"
    })

    paths = [
        # Tests Deduplication: 'tmp' key + 'tmp/local/files' in path
        PathTest("tmp/local/files/data.txt", "tmp/local/files/data.txt"),
        
        # Tests Logical Alias: 'out' key -> 'downloads' folder
        PathTest("out/file.txt", "downloads/file.txt"),
        
        # Tests Path Traversal Guard (Should fail)
        PathTest("tmp/../../../etc/passwd", "", is_valid=False),

        PathTest("tmp/tmp/local/files/test.txt", "tmp/local/files/test.txt")
    ]
    print("\n")
    for obj in paths:
        if not obj.is_valid:
            with pytest.raises(PermissionError):
                policy.resolve(obj.path)
        else:
            result = policy.resolve(obj.path)
            # Verify the result is absolute and ends with our expected structure
            assert result.is_absolute()
            assert str(result).endswith(obj.expected_suffix)
            if p:
                print(f"Input:\t{obj.path}")
                print(f"Result:\t{result}")
                print(f"Expect:\t{obj.expected_suffix}")


def test_policy_fails_on_missing_dir(tmp_path):
    fake_path = tmp_path / "missing_folder"

    with pytest.raises(FileNotFoundError) as execinfo:
        LocalFilePolicy({"bad_anchor":str(fake_path)})

    assert "FATAL" in str(execinfo.value)
    assert "bad_anchor" in str(execinfo.value)

def test_local_fs_round_trip(tmp_path, ed_journal):
    # define anchor dir
    anchor_dir = tmp_path / "data"
    anchor_dir.mkdir()

    # set policy
    policy = LocalFilePolicy({"data":str(anchor_dir)})
    
    # set logical path for data storage
    sink_path = Path("data/journal_edsm.log")

    test_payload = b"{username:username}"

    # Build Sink
    sink = LocalFileStream(
        resource_configuration=sink_path,
        policy=policy,
        chunk_size=1024,
        as_sink=True
    )

    # Write sink
    with sink:
        sink.write(Envelope(payload=test_payload))

    # Read
    
    source = sink.as_source()

    with source:
        envelopes = list(source.read())

    # Assertions
    assert len(envelopes) == 1
    assert envelopes[0].payload == test_payload
    assert envelopes[0].metadata["chunk_index"] == 0

def test_local_fs_line_reading(policy):
    """Verify the stream correctly yields individual lines."""
    logical_path = Path("data/multi_line.log")
    lines = [b"Line 1\n", b"Line 2\n", b"Line 3"]
    
    # 1. Setup multi-line file
    sink = LocalFileStream(logical_path, policy, chunk_size=1024, as_sink=True)
    with sink:
        for line in lines:
            sink.write(Envelope(payload=line))
            
    # 2. Read back using line-mode
    source = LocalFileStream(logical_path, policy, chunk_size=1024, use_lines=True)
    with source:
        results = list(source.read())
        
    assert len(results) == 3
    assert results[0].payload == b"Line 1\n"
    assert results[2].payload == b"Line 3"
    assert results[1].metadata["chunk_index"] == 1 # Verifies line counting

def test_local_fs_enforces_traversal_guard(policy):
    """Ensure the Stream cannot be initialized with a 'jailbreak' path."""
    # This tries to climb out of 'data' and into system files
    illegal_path = Path("data/../../etc/passwd")
    
    with pytest.raises(PermissionError) as excinfo:
        LocalFileStream(illegal_path, policy, chunk_size=1024)
        
    assert "PATH TRAVERSAL BLOCKED" in str(excinfo.value)

def test_sink_path_resolution_and_validation(policy):
    """
    Ensures that as_sink correctly resolves logical paths 
    and validates physical directory existence.
    """
    
    # CASE 1: Standard Logical Sink
    # This should resolve to {tmp_path}/data/journal_alpha.log
    logical_sink = LocalFileStream(
        resource_configuration=Path("data/journal_alpha.log"),
        policy=policy,
        chunk_size=1024,
        as_sink=True
    )
    
    # Verify internal state before opening
    assert logical_sink.mode == "wb"
    # The _resource_conf should be absolute now
    assert Path(logical_sink._resource_conf).is_absolute()
    assert "data/journal_alpha.log" in str(logical_sink._resource_conf)

    # CASE 2: The 'Missing Directory' Guard
    # We haven't created 'data/logs/', so this should fail on open()
    nested_path = Path("data/logs/journal_beta.log")
    sink_with_missing_dir = LocalFileStream(
        resource_configuration=nested_path,
        policy=policy,
        chunk_size=1024,
        as_sink=True
    )
    
    with pytest.raises(NotADirectoryError) as excinfo:
        sink_with_missing_dir.open()
    
    assert "Directory does NOT Exist" in str(excinfo.value)
    # Ensure it's reporting the PHYSICAL path in the error, not the logical one
    assert str(policy.get_anchor_path("data")) in str(excinfo.value)

def test_sink_idempotency(policy):
    """
    Ensures that if we pass an already resolved path back into a Sink,
    the policy doesn't blow up with a 'tmp' key error.
    """
    # 1. Get a resolved path
    resolved_path = policy.resolve("data/test.log")
    
    # 2. Try to create a Sink using that absolute path directly
    # This simulates what happens inside as_source() or similar hand-offs
    try:
        sink = LocalFileStream(
            resource_configuration=resolved_path,
            policy=policy,
            chunk_size=1024,
            as_sink=True
        )
    except PermissionError as e:
        pytest.fail(f"Sink failed to handle absolute path! Error: {e}")
        
    assert str(sink._resource_conf) == str(resolved_path)

def test_local_fs_cleanup_lifecycle(policy):
    """
    Verifies that file handles are strictly managed and 
    cleared from memory after use.
    """
    logical_path = "data/cleanup_test.log"
    stream = LocalFileStream(logical_path, policy, chunk_size=1024, as_sink=True)

    # 1. PRE-CONDITION: Handle should be None
    assert stream._file is None

    # 2. OPENED: Handle should exist
    with stream:
        assert stream._file is not None
        # Verify the OS-level file mode matches
        assert stream._file.mode == "wb"
        stream.write(Envelope(payload=b"Cleanup Check"))

    # 3. POST-CONDITION: Handle should be reset to None
    assert stream._file is None

def test_local_fs_manual_close(policy):
    """
    Verifies that calling .close() manually (outside context manager) 
    still cleans up the resource.
    """
    stream = LocalFileStream("data/manual.log", policy, chunk_size=1024, as_sink=True)
    
    stream.open()
    assert stream._file is not None
    
    stream.close()
    assert stream._file is None