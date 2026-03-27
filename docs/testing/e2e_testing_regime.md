# End-to-End (E2E) Testing Regime: ETL Pipeline v0.9

This document outlines the strategy, patterns, and infrastructure required to perform System Integration and End-to-End testing for the `etl-pipeline` framework within the Elite Dangerous community data ecosystem.

---

## 1. Definitions

### What is E2E in this Pipeline?
In a Hexagonal (Ports & Adapters) architecture, E2E testing verifies that the **Domain Logic** (Use Cases) correctly coordinates **Infrastructure Adapters** (HTTP, POSIX, PostgreSQL) to fulfill a complete user journey.

**The "Elite Dangerous" Journey:**
1.  **Ingress:** Download a `json.gz` file from a remote URL.
2.  **Integrity:** Verify checksums and decompress the stream.
3.  **Transformation:** Parse JSON packets and sample data.
4.  **Egress:** Generate PostgreSQL schemas and load the final records.

---

## 2. Recommended Directory Structure

To separate fast unit tests from slow, infrastructure-heavy E2E tests, use the following structure:

```text
tests/
├── unit/                   # Business logic, no IO.
├── integration/            # Tests individual adapters (e.g., PostgresAdapter).
└── e2e/                    # The "Whole Machine" tests.
    ├── conftest.py         # Shared fixtures (DB connections, Mock Server).
    ├── test_full_ingestion.py
    ├── data/               # Static assets for testing.
    │   └── samples/
    │       └── eddn_data.json.gz
    └── docker/             # Local test environment.
        ├── docker-compose.yml
        └── postgres/
            └── init.sql    # Baseline schema for tests.
```

---

## 3. Best Practices: Hexagonal Context

1.  **Dependency Inversion:** Never hardcode URLs or Connection Strings. Use the `SessionContext` and `AppConfig` to inject test values.
2.  **State Isolation:** Every E2E test should start with a clean database. Use `TRUNCATE` or Docker volume resets.
3.  **Observability:** Use the `traceability_provider` to verify that packets moved through the pipeline as expected (e.g., "Expected 1000 packets, got 1000").
4.  **Contract Testing:** Ensure that the `HttpContract` and `PosixFileContract` are strictly validated even in test environments.

---

## 4. Docker Environment (PostgreSQL + Mock Server)

This `docker-compose.yml` provides a real PostgreSQL instance and a lightweight Nginx container to simulate the remote EDDN server.

```yaml
# tests/e2e/docker/docker-compose.yml
version: '3.8'

services:
  # The Target Database
  test_db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: pipeline_test
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - ./postgres/init.sql:/docker-entrypoint-initdb.d/init.sql

  # The Mock Data Source (Simulates EDDN)
  mock_eddn:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ../data/samples:/usr/share/nginx/html:ro
```

---

## 5. Simulating the Pipeline Chain

To test "already downloaded" files while still using the `HttpAdapter`, we point the `HttpAdapter` to our `mock_eddn` service.

### Step 1: Prepare the Mock Data
Place your `eddn_data.json.gz` in `tests/e2e/data/samples/`.

### Step 2: The E2E Test Script (Pytest)
This script uses the `PipelineRunner` to execute a real flow.

```python
# tests/e2e/test_full_ingestion.py
import pytest
from src.app.use_cases.pipeline_runner import PipelineRunner
from src.app.domain.models.session_context import SessionContext

def test_remote_to_postgres_flow(stream_manager, engine_registry):
    # 1. Setup
    runner = PipelineRunner(stream_manager, engine_registry)
    context = SessionContext(trace_id="e2e-test-001")
    
    # We point to our LOCAL mock server instead of the real internet
    source_uri = "http://localhost:8080/eddn_data.json.gz"
    sink_uri = "postgresql://dev:password@localhost:5432/pipeline_test/commander_events"

    # 2. Execution
    runner.execute_pipeline(
        sources=[source_uri],
        sinks=[sink_uri],
        processors=[], # Add Checksum/Compression processors here
        session_context=context,
        engine_type="local"
    )

    # 3. Validation
    # Use a direct DB query to verify the data landed
    import psycopg2
    conn = psycopg2.connect("dbname=pipeline_test user=dev password=password host=localhost")
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM commander_events")
    count = cur.fetchone()[0]
    
    assert count > 0
    cur.close()
    conn.close()
```

---

## 6. Testing Strategy for Large Streams

*   **Sampling Pattern:** In your E2E test, pass a `SamplingMiddleware` to the `processors` list. This ensures you can run a "Full Chain" test on a 10GB file but only actually write 1MB to the database, saving time and disk space.
*   **Integrity Checks:** Since you are using `json.gz`, ensure your `HttpAdapter` is set to `HttpReadMode.RAW` or `BYTES`, and verify that the `DecompressionProcessor` emits valid JSON packets before they hit the database.
*   **Backpressure:** Monitor memory usage during the E2E run. The `HttpStream` and `PosixFileStream` are both `Iterator` based, so memory should remain flat even with massive files.
