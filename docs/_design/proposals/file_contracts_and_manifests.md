# File Contracts and Manifests

Concepts and Proposals for Tracking File / Stream *State* and generating *Contracts*

## Overview: Existing Frameworks and What They Use

1. **Do frameworks do Databases?**
Yes, almost all of them. Here are a few examples of how they handle "internal bookkeeping":

Apache Airflow: Uses a PostgreSQL or MySQL database to track every task instance, file location, and success/failure state.

Prefect / Dagster: Use similar backends to manage the "state" of the world.

DVC (Data Version Control): Uses a local SQLite DB or specialized sidecar files to track versions of large data files without checking the actual data into Git.

Delta Lake / Apache Iceberg: Instead of a DB, they use a Transaction Log (JSON/Parquet files) to track which files belong to which version of a table.

2. **The Pattern: The "File Registry"**
For your ETL pipeline, you are looking at the File Registry Pattern. Instead of just "hoping" a file exists in /srv/parquet, the framework maintains a "Source of Truth."

What you would track in a "Contract":
Lineage: Where did this file come from? (e.g., S3 -> Local -> Transformed).

Checksum/Hash: A unique finger-print (MD5/SHA) of the file to ensure it hasn't been tampered with or corrupted.

Schema Version: Which version of the DuckDB-inferred schema does this file adhere to?

Status: PENDING, PROCESSING, LOADED, or FAILED.

3. **Build vs. User Responsibility?**
In a well-designed framework, the Framework provides the Interface (Port), and the User provides the Storage (Adapter).

Framework's Job: Define the FileRegistry abstract class. Provide a default SQLiteFileRegistry or DuckDBFileRegistry that works out of the box for local Linux dev.

User's Job: If they move to production (AWS/GCP), they might implement a PostgresFileRegistry or DynamoDBFileRegistry so multiple servers can share the same state.

