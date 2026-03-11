# StreamFlow Architecture Map

## Application Summary
**StreamFlow** is a context-aware data streaming and pipeline orchestration framework built on Clean Architecture principles. It provides a unified interface for interacting with diverse storage protocols (Local POSIX, HTTP, etc.) while maintaining high traceability and type safety through its pipeline transformation engine.

### Core Architectural Patterns
- **Ports & Adapters (Hexagonal Architecture):** Decouples business logic from infrastructure.
- **Pipe-and-Filter:** Used in the Pipeline Subsystem for modular data transformation.
- **Fluent DSL:** Provided via `PipelineBuilder` for an expressive developer experience.
- **Smart Gateway Orchestrator:** `StreamManager` manages the lifecycle and resolution of resources.

---

## Component Status Table

| Component | Layer | Role | Status | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **StreamClient** | Application (Facade) | User entry point | 🟢 Partial | `pipeline()` method is a placeholder. |
| **StreamManager** | Application (Use Case) | Orchestrates resource lifecycle | 🟢 Complete | Core logic for handle resolution and policy checks. |
| **PipelineBuilder** | Application (Use Case) | DSL for pipeline definition | 🟢 Complete | Handles contract adjudication. |
| **PipelineRunner** | Application (Use Case) | Orchestrates pipeline execution | 🟢 Complete | Needs integration into `Bootstrap`. |
| **ResourceFactory** | Domain Service | Promotes URIs to Locations | 🟢 Complete | Handles Logical to Physical translation. |
| **ResourceCatalog** | Domain Service | Protocol/Boundary storage | 🟢 Complete | Stores protocol metadata. |
| **StreamRegistry** | Application (Registry) | Maps protocols to adapters | 🟢 Complete | Stores Adapter and Policy blueprints. |
| **EngineRegistry** | Application (Registry) | Stores pluggable execution engines | 🟡 Buggy | Naming mismatch (`get_engine` vs `get_engine_cls`). |
| **PipelineEngine** | Port (Output) | Execution Strategy Interface | 🟢 Complete | Abstract interface for engines. |
| **LocalPipelineEngine** | Infrastructure (Engine) | Sequential execution engine | 🔴 Missing | Implementation not found in `src/infrastructure/engines`. |
| **MiddlewareProcessor** | Port (Output) | Transformation Interface | 🟢 Complete | Unified interface for filters. |
| **ChecksumProcessor** | Infrastructure (Proc) | Verifies data integrity | 🟢 Complete | Example implementation of middleware. |
| **PosixFileStream** | Infrastructure (Adapter) | Local File System Adapter | 🟢 Complete | Protocol: `posix`, `file`. |
| **HttpStream** | Infrastructure (Adapter) | HTTP/S Remote Adapter | 🟢 Complete | Protocol: `http`, `https`. |

---

## System Architecture (Class Diagram)

```mermaid
classDiagram
    %% Core Orchestration
    class StreamClient {
        -StreamManager _manager
        -str _trace_id
        +get_handle(uri, as_sink, **settings) StreamHandle
        +pipeline(uri, **settings) PipelineBuilder
    }

    class StreamManager {
        -StreamRegistry _registry
        -ResourceFactory _factory
        -ResourceCatalog _catalog
        -AppConfig _app_config
        -SettingsResolver _resolver
        +get_handle(uri, as_sink, **settings) StreamHandle
        +read(uri, **settings) Iterator[Packet]
        +write(uri, data, **settings) None
    }

    class PipelineBuilder {
        -PipelineRunner _runner
        -List~str~ _source_uris
        -List~str~ _sink_uris
        -List~MiddlewareProcessor~ _processors
        +and_from(uri) PipelineBuilder
        +through(processor) PipelineBuilder
        +to(uri) PipelineBuilder
        +run(engine_type) None
    }

    class PipelineRunner {
        -StreamManager _manager
        -EngineRegistry _engine_registry
        +execute_pipeline(sources, sinks, processors, engine_type) None
    }

    %% Domain Models
    class StreamHandle {
        -IStreamAdapter _adapter
        -StreamCapacity _capacity
        -StreamContext _context
    }

    class PipelineBlueprint {
        +List~StreamHandle~ sources
        +List~StreamHandle~ sinks
        +List~MiddlewareProcessor~ processors
    }

    class Packet {
        +Payload payload
        +Metadata metadata
        +spawn(payload) Packet
    }

    %% Ports
    class IStreamAdapter {
        <<interface>>
        +read() Iterator[Packet]
        +write(data) None
        +close() None
    }

    class PipelineEngine {
        <<interface>>
        +setup(blueprint) PipelineEngine
        +execute() None
        +shutdown() None
    }

    class MiddlewareProcessor {
        <<interface>>
        +process(packet) Iterator[Packet]
        +flush() Iterator[Packet]
    }

    %% Infrastructure
    class LocalPipelineEngine {
        <<missing>>
        +execute()
    }

    class PosixFileStream {
        +read()
        +write()
    }

    %% Relationships
    StreamClient --> StreamManager : delegates
    StreamClient ..> PipelineBuilder : creates
    StreamManager --> ResourceFactory : uses
    StreamManager --> StreamRegistry : uses
    PipelineBuilder --> PipelineRunner : delegates
    PipelineRunner --> StreamManager : uses
    PipelineRunner --> EngineRegistry : uses
    PipelineRunner ..> PipelineBlueprint : creates
    PipelineRunner ..> PipelineEngine : invokes
    PipelineBlueprint --> StreamHandle : contains
    PipelineBlueprint --> MiddlewareProcessor : contains
    StreamHandle --> IStreamAdapter : wraps
    IStreamAdapter <|-- PosixFileStream
    PipelineEngine <|-- LocalPipelineEngine
```

---

## User Flow Diagram (System Entry)

This diagram maps the flow of a user requesting a resource handle or starting a pipeline through the `StreamClient`.

```mermaid
sequenceDiagram
    actor User
    participant SC as StreamClient
    participant SM as StreamManager
    participant RF as ResourceFactory
    participant SR as StreamRegistry
    participant SH as StreamHandle
    participant AD as IStreamAdapter

    User->>SC: get_handle(uri, as_sink=False)
    SC->>SM: get_handle(uri, as_sink=False)
    
    rect rgb(240, 240, 240)
    Note over SM, RF: Resource Resolution Phase
    SM->>RF: build(uri)
    RF-->>SM: StreamLocation (PhysicalPath/URI)
    end

    rect rgb(230, 240, 255)
    Note over SM, SR: Adapter Discovery Phase
    SM->>SR: get_registration(protocol)
    SR-->>SM: Blueprint (AdapterClass, Policy)
    end

    SM->>AD: instantiate(uri, context, policy)
    AD-->>SM: adapter instance

    SM->>SH: create(adapter, capacity, context)
    SH-->>SM: handle instance
    
    SM-->>SC: StreamHandle
    SC-->>User: StreamHandle

    User->>SH: __enter__()
    SH->>AD: open()
    SH-->>User: Stream Context
    
    User->>SH: read() / write()
    SH->>AD: read() / write()
    
    User->>SH: __exit__()
    SH->>AD: close()
```

---

## User Flow Diagram (Pipeline Building & Execution)

This diagram illustrates the fluent interface for constructing a pipeline and the subsequent orchestration of its execution.

```mermaid
sequenceDiagram
    actor User
    participant SC as StreamClient
    participant PB as PipelineBuilder
    participant PR as PipelineRunner
    participant SM as StreamManager
    participant ER as EngineRegistry
    participant PE as PipelineEngine
    participant BP as PipelineBlueprint

    User->>SC: pipeline(source_uri)
    SC->>PB: create(runner, source_uri, trace_id)
    SC-->>User: PipelineBuilder Instance

    loop Configuration Phase
        User->>PB: through(processor)
        Note over PB: Contract Adjudication (Type Check)
        PB-->>User: self (Fluent)
        
        User->>PB: to(sink_uri)
        PB-->>User: self (Fluent)
    end

    User->>PB: run(engine_type="local")
    PB->>PR: execute_pipeline(sources, sinks, processors, engine_type)

    rect rgb(240, 240, 240)
    Note over PR, SM: Handle Resolution Phase
    PR->>SM: get_handle(source_uri)
    SM-->>PR: Source StreamHandle
    PR->>SM: get_handle(sink_uri, as_sink=True)
    SM-->>PR: Sink StreamHandle
    end

    PR->>BP: create(sources, sinks, processors)
    BP-->>PR: PipelineBlueprint (Job Ticket)

    PR->>ER: get_engine_cls(engine_type)
    ER-->>PR: Engine Class

    PR->>PE: instantiate(trace_id)
    PR->>PE: setup(blueprint)
    
    rect rgb(230, 240, 255)
    Note over PR, PE: Execution Phase
    PR->>PE: __enter__()
    PR->>PE: execute()
    Note over PE: Data flows from Sources -> Processors -> Sinks
    PR->>PE: __exit__()
    PE->>PE: shutdown() (Closes all handles)
    end

    PR-->>PB: success/fail
    PB-->>User: Done
```

---

## Future Architecture (With ApplicationContext)

This section maps the planned transition to using the `AppContext` as the central runtime container for all system dependencies.

### Class Diagram (Evolution)

```mermaid
classDiagram
    class StreamClient {
        -AppContext _context
        -str _trace_id
        +get_handle(uri, as_sink, **settings) StreamHandle
        +pipeline(uri, **settings) PipelineBuilder
    }

    class AppContext {
        <<dataclass>>
        +StreamManager stream_manager
        +PipelineRunner pipeline_runner
        +StreamRegistry stream_registry
        +EngineRegistry engine_registry
        +SettingsResolver settings_resolver
        +ResourceCatalog resource_catalog
        +ResourceFactory resource_factory
        +TraceabilityProvider trace_provider
        +AppConfig config
    }

    class StreamManager {
        -StreamRegistry _registry
        -ResourceFactory _factory
        -ResourceCatalog _catalog
        -AppConfig _app_config
        -SettingsResolver _resolver
    }

    class PipelineRunner {
        -StreamManager _manager
        -EngineRegistry _engine_registry
    }

    StreamClient --> AppContext : holds
    AppContext --> StreamManager : contains
    AppContext --> PipelineRunner : contains
    AppContext --> StreamRegistry : contains
    AppContext --> EngineRegistry : contains
    AppContext --> ResourceFactory : contains
    PipelineRunner --> StreamManager : uses
```

### Bootstrapping Flow (With AppContext)

This diagram shows the "Big Bang" initialization process where all components are wired and injected into the `AppContext`.

```mermaid
sequenceDiagram
    participant App as App/Main
    participant B as Bootstrap
    participant R as Registries (Stream/Engine)
    participant S as Services (Catalog/Factory/Resolver)
    participant O as Orchestrators (Manager/Runner)
    participant AC as AppContext

    App->>B: initialize(config_overrides)
    
    activate B
    B->>R: create & register adapters/engines
    B->>S: create Catalog, Factory, Resolver
    
    rect rgb(240, 240, 240)
    Note over B, O: Dependency Injection Phase
    B->>O: instantiate StreamManager(Registry, Factory, Catalog, Config, Resolver)
    B->>O: instantiate PipelineRunner(Manager, EngineRegistry)
    end

    B->>AC: instantiate AppContext(Manager, Runner, Registries, Services, Config)
    AC-->>B: context instance
    
    B-->>App: AppContext
    deactivate B

    Note over App, AC: System is Ready
```

### Planned Refactoring Changes (ApplicationContext)

The transition to the `AppContext` will involve the following specific implementation changes:

1.  **Bootstrap Return Type:** `Bootstrap.initialize()` will be refactored to return the `AppContext` dataclass instead of a raw `StreamManager`.
2.  **StreamClient Internal State:** `StreamClient` will replace its `self._manager` reference with `self._context: AppContext`.
3.  **Pipeline Subsystem Wiring:** The `PipelineRunner` and `EngineRegistry` will be initialized and wired within `Bootstrap`, ensuring they are correctly injected into the `AppContext`.
4.  **Facade Delegation:** `StreamClient` convenience methods (`read`, `write`, `get_handle`) will be updated to delegate to `self._context.stream_manager`.
5.  **Pipeline Builder Integration:** The `StreamClient.pipeline()` method will be fully implemented, using `self._context.pipeline_runner` to instantiate the `PipelineBuilder`.
6.  **Dependency Transparency:** Services like `ResourceCatalog`, `SettingsResolver`, and `ResourceFactory` will be explicitly accessible via the `AppContext`, making the system easier to test and extend.
7.  **Engine Registration:** A concrete `LocalPipelineEngine` will be registered in the `EngineRegistry` during the bootstrapping phase to enable actual data processing.

---

## Technical Debt & Observation Log

1.  **Pipeline Subsystem Disconnect:** The `PipelineRunner` and `EngineRegistry` are defined but not wired into the `Bootstrap.initialize` or the `StreamClient`.
2.  **Engine Implementation Gap:** There is no concrete implementation of `PipelineEngine` (e.g., `LocalPipelineEngine`) to perform actual work.
3.  **EngineRegistry Bug:** The `PipelineRunner` calls `get_engine_cls` while the `EngineRegistry` defines `get_engine`.
4.  **Incomplete StreamClient Facade:** `StreamClient.pipeline()` remains a placeholder, preventing user-facing access to the pipeline builder.
5.  **Empty Infrastructure Engine Directory:** `src/infrastructure/engines` is currently empty.
