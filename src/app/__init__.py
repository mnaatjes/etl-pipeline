# src/app/__init__.py

"""
src/
└── app/
    ├── domain/               <-- THE CORE (The "What")
    │   ├── models/           # Nouns: Dataclasses, Enums (e.g., Environment, Record)
    │   ├── exceptions.py     # Domain-specific errors (e.g., ProcessingError)
    │   └── services/         # Pure logic that doesn't fit in a single model
    │
    ├── ports/                <-- THE BOUNDARY (The "How")
    │   ├── input/            # Interfaces for those calling the app (e.g., IManager)
    │   └── output/           # Interfaces for tools the app uses (e.g., IDataStream, IRepository)
    │
    ├── use_cases/            <-- THE ORCHESTRATION (The "Why")
    │   ├── jobs/             # Specific ETL flows (e.g., base.py, sync_job.py)
    │   └── manager.py        # The coordinator/facade
    │
    ├── bootstrap.py          # Dependency Injection: Wiring Adapters to Ports
    └── __init__.py           # Facade functions (e.g., bootstrap_pipeline())
    
└── infrastructure/           <-- THE ADAPTERS (The "Tools")
    ├── adapters/
    │   ├── streams/          # Concrete implementations (e.g., HttpAdapter, DbAdapter)
    │   ├── persistence/      # DB specific logic (SQLAlchemy, Motor, etc.)
    │   └── telemetry/        # External logging/metrics (Prometheus, CloudWatch)
    ├── config/               # Reading Linux Env/YAML into AppConfig models
    └── entrypoints/          # The "Drivers": CLI, Web Server, Cron Job
"""

