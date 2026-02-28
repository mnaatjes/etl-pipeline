# tests/unit/test_remote_http_stream.py
import pytest
import respx
from respx.router import MockRouter
import httpx
from src.infrastructure import RemoteHttpStream
from src.app.ports.envelope import Envelope, RegimeType

def test_http_stream_lifecycle(respx_mock):
    # Create mock uri
    url = "https://eddn.elite/api/vi/latest"
    mock_data = b"Data Chunks from Eddn 01"

    # 1. Mock HEAD request for .exists()

    # For HEAD
    respx_mock.head(url).mock(return_value=httpx.Response(
        200,
        headers={
            "Content-Type":"application/octet-stream",
            "Content-Length":"1048576"
        }
    ))

    # For GET
    respx_mock.get(url).mock(return_value=httpx.Response(
        200,
        headers={
            "Content-Type":"application/octet-stream",
            "Content-Length":"1048576",
            "Content-Encoding":"identity"
        },
        content=mock_data
    ))

    # Assign Stream
    stream = RemoteHttpStream(url, chunk_size=1024)

    # 2. Evaluate HEAD Request: exists()
    assert stream.exists()

    # Collect Sent headers for Debugging
    HEAD_headers = respx_mock.calls.last.response.headers
    #print(HEAD_headers)

    # 3. Evaluate GET Request: open()
    with stream:
        packets = list(stream.read())
         # Assertions
        assert len(packets) == 1
        envelope = packets[0]
        assert envelope.payload == mock_data
        assert envelope.regime == RegimeType.BYTES
    
    # 4. Verify Cleanup
    assert stream._client is None
    assert stream._response is None
            

    GET_headers = respx_mock.calls.last.response.headers
    #print(GET_headers)

def test_remote_http_lines_reading(respx_mock):
    """Verifies that HTTP streams correctly yield lines"""
    # Define Props
    url = "https://eddn.elite/api/stream"
    mock_lines = b'{"msg": "line1"}\n{"msg": "line2"}'

    # Mock GET
    respx_mock.get(url).mock(return_value=httpx.Response(200, content=mock_lines))
    stream = RemoteHttpStream(url, chunk_size=1024, use_lines=True)

    # Open and Read
    with stream:
        packets = list(stream.read())

    # Assertions
    assert len(packets) == 2
    env = packets[0]
    assert isinstance(env.payload, bytes)
    assert b"line1" in env.payload

def test_http_stream_handles_errors(respx_mock):
    """Ensures the stream raises appropriate errors for 404 responses."""
    url = "https://eddn.elite/api/broken"
    respx_mock.get(url).mock(return_value=httpx.Response(404))

    stream = RemoteHttpStream(url, chunk_size=1024)

    # Since your open() calls self._response.raise_for_status()
    with pytest.raises(httpx.HTTPStatusError):
        with stream:
            pass

def test_http_header_collection(respx_mock):
    url = "https://eddn.elite/api/v1/latest"

    # Mock specific headers
    respx_mock.get(url).mock(return_value=httpx.Response(
        200,
        content=b"here is some data",
        headers={
            "Content-Type":"application/json",
            "X-EDDN-Version": "1.0"
        }
    ))

    # Make Stream
    # Perform open()
    stream = RemoteHttpStream(url, chunk_size=1024)
    with stream:
        assert stream._response is not None
        assert stream._response.headers["Content-Type"] == "application/json"
        assert stream._response.headers.get("X-EDDN-Version") == "1.0"

def test_http_format_conversion(respx_mock):
    """Even if server SENDS JSON str the stream YIELDS bytes"""
    # URI
    url = "https://eddn.elite/api/json"
    # Mock JSON Response
    respx_mock.get(url).mock(return_value=httpx.Response(200, json={"status":"ok"}))

    # init stream open()
    stream = RemoteHttpStream(url, chunk_size=1024)
    with stream:
        packets = list(stream.read())
        # Assertions
        env = packets[0]
        assert isinstance(env.payload, bytes)
        assert b'"status":"ok"' in env.payload

def test_http_wrong_content_logic(respx_mock):
    """Simulates 200OK with content body of Type:Empty"""
    url = "https://eddn.elite/api/empty"
    respx_mock.get(url).mock(return_value=httpx.Response(200, content=b""))
    stream = RemoteHttpStream(url, chunk_size=1024)

    with stream:
        packets = list(stream.read())
        assert len(packets) == 0

def test_http_content_type_assertion(respx_mock):
    """
    Verifies Detection of Mismatch formats
    - Expects: Anything Else - Catching Content-Type to perform action
    - Response: HTML
    """
    url = "https://eddn.elite/api/data"

    respx_mock.get(url).mock(return_value=httpx.Response(
        200,
        headers={
            "Content-Type":"text/html"
        },
        content=b"<html><head><title>This is a website title</title></head><body>Hello World</body></html>"
    ))

    stream = RemoteHttpStream(url, chunk_size=1024)
    with stream:
        assert stream._response is not None
        content_type = stream._response.headers.get("Content-Type")
        assert "text/html" in content_type

def test_http_encoding(respx_mock):
    """Verify that httpx is handling Encoding Correctly"""
    url = "https://eddn.elite/api/text"

    # Mock Response with Specific Charset
    respx_mock.get(url).mock(return_value=httpx.Response(
        200,
        headers={"Content-Type":"text/plain; charset=iso-8859-1"},
        content="Céline".encode("iso-8859-1")
    ))
    
    stream = RemoteHttpStream(url, chunk_size=1024)
    with stream:
        assert stream._response is not None
        assert stream._response.encoding == "iso-8859-1"

def test_http_timeout_handling(respx_mock):
    """Tests Timeout and raises TimeoutException"""
    url = "https://eddn.elite/slow-api"

    # Simulate Timeout Error
    respx_mock.get(url).mock(side_effect=httpx.TimeoutException("Server mucho Slow, Esse!"))

    # Execute
    stream = RemoteHttpStream(url, chunk_size=1024)

    with pytest.raises(httpx.TimeoutException) as excinfo:
        with stream:
            pass
    
    # Readout
    #print(f"Timeout Exception raised for url: {url}")

def test_http_wrong_content_type(respx_mock: MockRouter):
    """Try to read lines on non-image.jpg source output"""
    url = "https://eddn.elite/image.jpg"

    # Send binary garbage that has no newlines
    binary_payload = b"\xff\xd8\xff\xe0\x00\x10JFIF"
    respx_mock.get(url).mock(return_value=httpx.Response(
        200,
        headers={"Content-Type":"image/jpeg"},
        content=binary_payload
    ))

    # Tell stream to read line:
    # DO NOT USE use_lines=True for Images
    stream = RemoteHttpStream(url, chunk_size=1024, use_lines=True)

    with stream:
        packets = list(stream.read())
        # Won't crash
        # Will yield a binary blob as 1 line
        assert len(packets) == 1

def test_jpeg_as_binary_chunks(respx_mock):
    url = "https://eddn.elite/cmdr_avatar.jpg"
    # A fake JPEG header (SOI marker) followed by random "image" bytes
    jpeg_data = b"\xff\xd8\xff\x00\x01\x02\x03\x04\x05\x06\x07\x08"
    
    respx_mock.get(url).mock(return_value=httpx.Response(
        200, content=jpeg_data, headers={"Content-Type": "image/jpeg"}
    ))

    # Path B: Standard block buffering (The CORRECT way for JPEGs)
    stream = RemoteHttpStream(url, chunk_size=4) # Small chunks to force split
    
    with stream:
        envelopes = list(stream.read())

    # 12 bytes total / 4 byte chunks = 3 Envelopes
    assert len(envelopes) == 3
    assert envelopes[0].payload == b"\xff\xd8\xff\x00"
    assert envelopes[0].metadata["stream_mode"] == "block_buffered"

def test_jpeg_misused_as_lines(respx_mock):
    url = "https://eddn.elite/misconfigured.jpg"
    # JPEG data that accidentally contains a 0x0A (Newline) byte
    # bytes: [FF, D8, 0A, FF] -> The 0A is 'newline' in ASCII
    tricky_data = b"\xff\xd8\x0a\xff" 
    
    respx_mock.get(url).mock(return_value=httpx.Response(200, content=tricky_data))

    # Path A: Line buffering (The INCORRECT way for JPEGs)
    stream = RemoteHttpStream(url, chunk_size=1024, use_lines=True)
    
    with pytest.raises(AssertionError) as info:
        with stream:
            envelopes = list(stream.read())

        # Because iter_lines() found that 0x0A, it split the "image" into two lines!
        # This is why 'use_lines' is dangerous for binary.
        assert len(envelopes) == 2
        assert envelopes[0].payload == b"\xff\xd8" # Cut off before the newline byte
