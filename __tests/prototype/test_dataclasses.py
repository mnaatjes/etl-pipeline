# tests/prototype/test_dataclasses.py
import pytest
from uuid import uuid4
from dataclasses import dataclass, field

@dataclass
class StreamConfig:
    id: str = field(default_factory=lambda: str(uuid4())[:12])
    items: list = field(default_factory=list)
    tags: list = field(default_factory=list)
    url:str = "https://eddn.elite/api/latest/data"
    size: int = 4
    chunk_size:int = 1024
    retries: int = 3
    user_agent: str = "ElitePipeline/1.0"
    squared: int = field(init=False)

    def __post_init__(self):
        self.squared = self.size ** 2


def test_type_hinting():

    def config(props:StreamConfig): 
        return props

    result = config(StreamConfig(
        url="https://eddn.elite/api/v1/data",
        size=1024
    ))

    assert isinstance(result.squared, int)
    assert result.size == 1024
    assert result.squared == 1048576
    #config(props=StreamConfig(url="https://eddn.elite/api/v1/data", size=1024))

def test_list_isolation():
    conf = StreamConfig(items=["diamondback explorer", "diamondback scout", "Sol"])
    settings = StreamConfig(items=["Pioneer Station", "Raz Gateway", "Sol"])
    actual = [x for x in conf.items if x in settings.items]
    assert "Sol" in actual
    assert conf.id != settings.id
    