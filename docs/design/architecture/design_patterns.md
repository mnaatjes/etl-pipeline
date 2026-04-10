# Design Patterns and Architectural Roles

The pipeline engine utilizes several established software design patterns to achieve high flexibility, testability, and maintainability.

## 1. Interactor Pattern (The Job)
The `LinearJob` acts as an **Interactor** in Clean Architecture. It encapsulates a specific business use case (moving data from A to B) and sits at the center of the application logic, independent of infrastructure details.

## 2. Abstract Factory Pattern (StreamManager)
The `StreamManager` provides an interface for creating families of related objects (`DataStreams`) without specifying their concrete classes (Local, HTTP, etc.). It abstracts away the complexity of stream initialization.

## 3. Decorator / Pipeline Pattern (Middleware)
The middleware chain is a functional implementation of the **Pipeline Pattern**. Each processor "wraps" or "transforms" the data (the Envelope) before handing it to the next step. The `LinearJob` acts as the engine driving data through this pipeline.

## 4. Strategy Pattern (SettingsResolver)
The `SettingsResolver` encapsulates the "algorithm" for resolving configuration (the 3-tier Waterfall). This allows the logic of how settings are merged to be changed or extended without affecting the `StreamManager` or the `DataStreams`.

## 5. Bridge Pattern (Infrastructure Decoupling)
By using the **Bridge Pattern**, the `LinearJob` (Logic) is decoupled from the `StreamManager` (Infrastructure). The Job only knows about the `DataStream` interface, allowing it to work with any stream provided at runtime.

## Summary of Best Practices
- **Stateless Orchestrators:** Jobs are stateless; they perform a task and disappear.
- **Dependency Flow:** Components flow from high-level rules (`AppConfig`) to specific executors (`Jobs`).
- **Testability:** The separation allows for unit testing the `SettingsResolver` without networking, and testing `Jobs` using simple list-backed mock streams.
