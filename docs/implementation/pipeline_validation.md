# Pipeline Configuration Validation

The `_validate_contracts()` method is an **Architectural Guard** called during `Pipeline.__init__`. It ensures that a sequence of processors matches in terms of their input and output "Regimes," preventing runtime crashes.

---

## 1. The Strategy: Regime Metadata

To make validation work, each middleware class must "declare" its regime. This allows the pipeline to "see" the regime of each processor without actually running it.

### Update the Middleware Port (`src/app/ports/middleware.py`)
Add `input_regime` and `output_regime` properties to the base classes.

```python
class ByteMiddleware(Middleware):
    input_regime = "BYTES"
    output_regime = "BYTES"

class ObjectMiddleware(Middleware):
    input_regime = "OBJECT"
    output_regime = "OBJECT"
    
class JsonToBytes(Middleware):
    input_regime = "OBJECT"
    output_regime = "BYTES"
```

---

## 2. Implementation: `_validate_contracts()`

The method walks through the list of processors and compares the expected output of Step A with the expected input of Step B.

```python
def _validate_contracts(self):
    """Ensures that the output of each middleware matches the input of the next."""
    if not self.processors:
        return

    # We assume the source yields BYTES by default
    current_regime = "BYTES"

    for i, proc in enumerate(self.processors):
        # 1. Check if the processor has the required metadata
        in_type = getattr(proc, 'input_regime', "ANY")
        out_type = getattr(proc, 'output_regime', "ANY")

        # 2. Validate the 'handshake'
        if in_type != "ANY" and in_type != current_regime:
            raise ValueError(
                f"Pipeline Configuration Error at index {i}: "
                f"Processor '{proc.__class__.__name__}' expects {in_type}, "
                f"but the previous step is providing {current_regime}."
            )

        # 3. Update the regime for the next iteration (unless it's ANY)
        if out_type != "ANY":
            current_regime = out_type
```

---

## 3. Logical vs. Illogical Sequences

### ❌ The Illogical Sequence (Crashes Runtime)
```python
processors = [
    SHA256Hasher(),    # Regime: BYTES -> BYTES
    FieldMapper()      # Regime: OBJECT -> OBJECT
]
# Result: Error! FieldMapper expects OBJECT, but SHA256Hasher provides BYTES.
```

### ✅ The Logical Sequence (Safe)
```python
processors = [
    SHA256Hasher(),    # Regime: BYTES -> BYTES
    JsonToDict(),      # Regime: BYTES -> OBJECT (The Bridge)
    FieldMapper(),     # Regime: OBJECT -> OBJECT
    DictToJson()       # Regime: OBJECT -> BYTES (The Bridge)
]
# Result: Validation Passes.
```

---

## 4. Best Practices for Validation

*   **Avoid Over-Engineering**: Do not try to validate internal dictionary keys or deep data structure schemas during initialization. Stick to the **Regime** (Bytes vs. Object).
*   **Static Checks Only**: Do not pass actual data through processors during validation.
*   **Handle "ANY"**: Label middleware like `Logger` or `Profiler` as `ANY` so the validator skips them and keeps the previous regime active.
*   **Compiler-like Action**: Think of `_validate_contracts()` as a compiler for the pipeline configuration, catching "grammar" errors before long-running transfers.
