# tests/unit/test_evaluate_urls.py
import pytest
from src.infrastructure.decorators.http_probe import HttpHeaderProbeDecorator
from src import app

def test_urls_registration(stream_registry, remote_url):
    source = stream_registry.get_stream(remote_url)

    try:
        with source:
            iterator = source.read()
            env = next(iterator)
            #print(env)
    except StopIteration:
        #print(f"\nStream at {remote_url} returned no data")
        pass
    except Exception as e:
        #print(f"\nFailed to read from {remote_url}: {e}")
        pass

def test_urls_decorrated(stream_registry, remote_url):
    http_source = stream_registry.get_stream(remote_url)
    source   = HttpHeaderProbeDecorator(http_source)

    try:
        with source:
            iterator = source.read()
            envelope = next(iterator)
            
    except StopIteration:
        #print(f"\nStream at {remote_url} returned no data")
        pass
    except Exception as e:
        #print(f"\nFailed to read from {remote_url}: {e}")
        pass