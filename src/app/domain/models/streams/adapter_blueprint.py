# src/app/domain/models/streams/adapter_blueprint.py

from dataclasses import dataclass
from typing import Optional, Type

from src.app.ports.output.datastream import DataStream
from src.app.ports.output.stream_policy import StreamPolicy
from src.app.ports.input.resource_boundary import ResourceBoundary

@dataclass
class AdapterBlueprint:
    protocol: str
    adapter_cls: Type[DataStream]
    policy: Optional[StreamPolicy] = None
    boundary: Optional[ResourceBoundary] = None