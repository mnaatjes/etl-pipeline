# Layered Entry Implementation Details

This document outlines the implementation of the Registry, Manager, and the "Elite" Plugin-Ready Bootstrap system.

## 1. The Registry (The Catalog)

The registry avoids hardcoding streams, allowing for custom protocols.

```python
# src/app/services/stream_registry.py
from typing import Type
# Note: DataStream would be imported from your ports/base

class StreamRegistry:
    def __init__(self):
        self._protocols: dict[str, Type[DataStream]] = {}

    def register(self, protocol: str, adapter_cls: Type[DataStream]):
        self._protocols[protocol] = adapter_cls

    def get_adapter(self, uri: str) -> Type[DataStream]:
        proto = uri.split("://")[0]
        if proto not in self._protocols:
            raise ValueError(f"Unsupported protocol: {proto}")
        return self._protocols[proto]
```

## 2. The Manager (The Settings Resolver)

The Manager handles the 3-Tier Waterfall: Global Config + Protocol Defaults + User Overrides.

```python
# src/app/services/stream_manager.py
class StreamManager:
    def __init__(self, registry: StreamRegistry, global_config: dict):
        self.registry = registry
        self.global_config = global_config

    def create_stream(self, uri: str, as_sink: bool = False, **overrides) -> DataStream:
        adapter_cls = self.registry.get_adapter(uri)
        
        # 1. Start with Global Config (Tier 1)
        # 2. Layer on Overrides (Tier 3)
        # Note: The DataStream base class handles Tier 2 (Protocol Defaults) 
        # via the settings_contract dataclass defaults!
        settings = {**self.global_config, **overrides}
        
        return adapter_cls(uri=uri, as_sink=as_sink, **settings)
```

## 3. The Plugin-Ready Bootstrap

Using `importlib.metadata` for auto-discovery of external plugins.

```python
# src/app/services/bootstrap.py
import importlib.metadata
from src.app.services.stream_registry import StreamRegistry

class Bootstrap:
    @staticmethod
    def initialize_registry() -> StreamRegistry:
        registry = StreamRegistry()
        
        # 1. Register Internal (Core) Streams
        from src.infrastructure.streams.http.adapter import RemoteHttpStream
        registry.register("http", RemoteHttpStream)
        registry.register("https", RemoteHttpStream)

        # 2. Auto-Discover External Plugins
        group = "etl_pipeline.streams"
        entry_points = importlib.metadata.entry_points().select(group=group)
        
        for entry_point in entry_points:
            adapter_cls = entry_point.load()
            registry.register(entry_point.name, adapter_cls)
            
        return registry
```

## 4. Defining a Plugin (pyproject.toml)

External packages announce their streams in their configuration.

```toml
# In the plugin's pyproject.toml
[project.entry-points."etl_pipeline.streams"]
s3 = "my_plugin_package.s3_adapter:S3DataStream"
redis = "my_plugin_package.redis_adapter:RedisDataStream"
```

## 5. The Unified Facade (The Client)

```python
# src/etl_pipeline/client.py
from src.app.services.bootstrap import Bootstrap
from src.app.services.stream_manager import StreamManager

class EtlClient:
    def __init__(self, config_dict: dict = None):
        # 1. Bootstrap the Registry (Discovery)
        self._registry = Bootstrap.initialize_registry()
        
        # 2. Initialize the Manager with Global Config (Tier 1)
        self._manager = StreamManager(
            registry=self._registry, 
            global_config=config_dict or {}
        )

    def stream(self, uri: str, as_sink: bool = False, **overrides) -> DataStream:
        """The clean user entry point."""
        return self._manager.create_stream(uri, as_sink, **overrides)
```
