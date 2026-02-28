# tests/conftest.py
import pytest
from typing import Optional, Any
from datetime import datetime
from dataclasses import dataclass, field

# 1. Import from the 'app' layer (Interfaces & Logic)
from src.app import DataStream, BasePolicy, middleware

# 2. Import from the 'infrastructure' layer (Implementations)
from src import infrastructure as infra

@dataclass
class Config:
    dir: dict[str,str]
    chunk_size:Optional[int] = 1024
    http:Optional[dict[str,Any]] = field(
        default_factory=lambda: {
    "max_connections":2,
    "max_keepalive":1,
    "timeout":10
    })

@pytest.fixture(scope="session")
def test_data():
    return [
        {"url":"downloads", "exp":True},
        {"url":"downloads/file.json", "exp":True},
        {"url":"file://downloads/file.json", "exp":True},
        {"url":"file:///downloads/file.json", "exp":True},
        {"url":"file:///srv/pipeline/tests/data/downloads/file.json", "exp":True},
    ]
@pytest.fixture(scope="session")
def settings():
    return Config({
        "downloads":"tests/data/downloads"
    })

@pytest.fixture(scope="session")
def file_policy(settings):
    return infra.LocalFilePolicy(settings.dir)

@pytest.fixture(scope="session")
def stream_registry(settings, file_policy):
    # 1. Create Instance of Registry
    reg = infra.StreamRegistry(settings.chunk_size)
    # 2. Bootstrap Protocol Dataclasses
    reg.register("https", infra.RemoteHttpStream)
    reg.register("http", infra.RemoteHttpStream)
    reg.register(
        protocol="file",
        adapter_cls=infra.LocalFileStream,
        policy=file_policy,
    )

    # Return
    return reg

@pytest.fixture(scope="session")
def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%I%S")

@pytest.fixture(scope="session")
def http_source(stream_registry):
    return stream_registry.get_stream("https://jsonplaceholder.typicode.com/posts")

@pytest.fixture(scope="session")
def local_sink_json(stream_registry, timestamp):
    return stream_registry.get_stream(f"file:///srv/pipeline/tests/data/downloads/sink_{timestamp}.json", as_sink=True)

@pytest.fixture(scope="session")
def local_sink_bin(stream_registry, timestamp):
    return stream_registry.get_stream(f"file:///srv/pipeline/tests/data/downloads/sink_{timestamp}.bin", as_sink=True)

@pytest.fixture(params=[
    # --- Standard API Mocks (JSON Objects) ---
    "https://jsonplaceholder.typicode.com/posts",
    "https://jsonplaceholder.typicode.com/comments",
    "https://dummyjson.com/products",
    "https://dummyjson.com/quotes",
    "https://reqres.in/api/users?page=2",

    # --- Live Public Data (Real-World Complexity) ---
    "https://openlibrary.org/search.json?q=the+lord+of+the+rings",
    "https://api.spacexdata.com/v4/launches/latest",
    "https://api.github.com/events",

    # --- Bulk Data & Streams (Large Payloads) ---
    "https://api.nobelprize.org/v1/prize.json",
    "https://data.nasa.gov/resource/gh4g-9sfh.json",
    "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson",

    # --- Network/Format Testing ---
    "http://httpbin.org/json",       # Valid JSON
    "http://httpbin.org/bytes/1024"  # Raw bytes (To test your ByteStream robustness)
])
def remote_url(request):
    return request.param

@pytest.fixture(scope="session")
def ed_journal():
    return {
        "timestamp": "2026-02-26T14:21:00Z",
        "event": "FSDJump",
        "StarSystem": "Shinrarta Dezhra",
        "SystemAddress": 3932277478106,
        "StarPos": [44.75000, -9.50000, -59.40625],
        "Body": "Shinrarta Dezhra",
        "JumpDist": 15.242,
        "FuelUsed": 2.140521,
        "FuelLevel": 28.520412,
        "SystemFaction": {
            "Name": "The Pilots Federation",
            "FactionState": "None"
        },
        "SystemSecurity": "$GAlAXY_MAP_INFO_state_lawless;",
        "SystemEconomy": "$economy_HighTech;",
        "SystemSecondEconomy": "$economy_Industrial;",
        "Powers": ["Li Yong-Rui"],
        "PowerplayState": "Exploited"
    }