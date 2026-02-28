# Layered Entry Strategy

To transition the refactored DataStream into a production-ready library, we employ a "Layered Entry" strategy. The goal is to encapsulate the complexity of settings merging (The Waterfall) and protocol mapping (The Registry) behind a clean, intuitive Facade.

## 1. The Architectural Flow

The user interacts with a single "Entry Point," while the heavy lifting happens in the background.

| Component | Responsibility | Analog |
| :--- | :--- | :--- |
| **Facade (StreamClient)** | The public API. Simple methods like `get_stream()`. | The Concierge |
| **Bootstrap** | Loads environment variables, YAML configs, and registers adapters. | The Foundation |
| **StreamRegistry** | Maps protocols (s3://, http://) to DataStream classes. | The Catalog |
| **StreamManager** | The "Brain." It merges the 3-Tier settings and requests the stream. | The Architect |

## 2. User Experience (The "ProDesk" Way)

A user (or a main script) uses the library with zero friction:

```python
from my_etl_library import EtlClient

# 1. Initialize once
client = EtlClient(config_path="config.yaml")

# 2. Use anywhere
with client.stream("http://api.data.com/v1", timeout=60) as stream:
    for envelope in stream.read():
        print(envelope.payload)
```

## 3. Why This Works

- **Encapsulation:** The user never sees the `StreamContract` or the `Generic[T]` logic. It just works.
- **Extensibility:** If you want to add a `PostgresStream` tomorrow, you just register it in the Bootstrap layer. The Facade and Manager remain untouched.
- **Testability:** You can easily swap the `StreamRegistry` with a mock registry for unit testing high-level business logic.
- **Zero Maintenance:** With the plugin system, you stop being the bottleneck. New streams can be added by installing a package.
- **Clean Dependencies:** The core DataStream package doesn't need to import external dependencies (like `boto3` or `redis-py`). Those stay inside the plugins.
