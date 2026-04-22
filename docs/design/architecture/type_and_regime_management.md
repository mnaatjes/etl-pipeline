# Type and Regime Management

Managing evolving types in a streaming pipeline is essentially managing a State Machine. On a resource-constrained environment like the Linux ProDesk, the primary goal is to prevent **"Type Drift"**—where the system loses track of whether data is a raw buffer or a structured object.

## Core Concepts

### Regimes
Data travels through the pipeline in distinct "Regimes":
1.  **Byte Regime**: Raw data (e.g., `bytes`) suitable for hashing, encryption, or disk I/O.
2.  **Object Regime**: Structured data (e.g., `dict`, `list`) suitable for mapping, filtering, or transformation.

### The "Bridge"
A specific type of middleware responsible for transitioning between regimes (e.g., `JsonToDict` or `DictToJson`).

---

## Design Patterns

### 1. Chain of Responsibility with Type Guards
Middleware should explicitly declare their expected input type. Never let a middleware "guess" the data format.
*   **Best Practice**: Use "Converter" or "Adapter" middleware to explicitly bridge regimes.
*   **Pattern**: If a `SHA256Hasher` (Byte) needs to follow a `FieldMapper` (Object), you must insert a `JsonToBytes` (Converter) between them.

### 2. The "Envelope" Pattern (DTO)
Instead of passing naked data, pass a Container Object (Data Transfer Object).
*   **The Concept**: Pass an object with a `.payload` (the data) and a `.regime` (the type label).
*   **Why it works**: You can attach metadata (timestamps, source URLs) that stays with the data even after conversion.

---

## Best Practices

*   **Regime Grouping**: Visually group middleware in configuration to make transitions obvious.
*   **Fail Fast**: Strict enforcement of types at runtime. If a contract is violated, the pipeline should crash immediately rather than attempting to "coerce" types.
*   **None as a Filter**: Use `None` explicitly to signal that a chunk should be dropped. Type hints should reflect this: `Envelope | None`.
*   **Memory Efficiency**: Keep the "Object Regime" as short as possible. Parse, map, and re-serialize quickly to return to the "Byte Regime," which is easier for Linux to buffer and move to disk.

---

## Anti-Patterns to Avoid

*   **❌ The God Middleware**: Single components handling multiple disparate tasks (e.g., `TransformAndHashAndSave`). This makes type validation impossible.
*   **❌ Hidden Side Effects**: Middleware should be Pure Functions. Avoid modifying global state or interacting with the Sink prematurely.
*   **❌ Ambiguous Coercion**: Middleware that tries to `json.loads()` if it gets bytes but passes if it gets a dict. This leads to unpredictable behavior.
