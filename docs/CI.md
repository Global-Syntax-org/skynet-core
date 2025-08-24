CI and Integration Tests

This document describes the project's CI setup and how to run integration tests, including optional MSSQL tests.

Unit tests (fast)
- Workflow: `.github/workflows/ci-unit-tests.yml`
- Runs on push and pull requests to `main`.
- Installs `requirements.txt` (or falls back to a minimal test install) and runs `pytest`.
- Tests included: `tests/test_storage_fullstack.py` (Memory, File, SQLite adapters). The SQLite tests require `aiosqlite` to be available; the job installs test deps.

MSSQL integration tests (manual / heavy)
- Workflow: `.github/workflows/ci-mssql-integration.yml`
- Trigger: manual dispatch (workflow_dispatch) because the job requires system-level ODBC drivers and a running SQL Server.
- Requirements:
  - Set a repository secret `MSSQL_SA_PASSWORD` with a strong SA password before running the workflow.
  - The workflow starts a SQL Server Docker container (image: `mcr.microsoft.com/mssql/server:2019-latest`) and installs the Microsoft ODBC driver (`msodbcsql17`) and `unixodbc-dev`.
  - The workflow installs `pyodbc` and `aioodbc` and runs `tests/test_storage_mssql.py`.

Running MSSQL tests locally
1. Install system ODBC driver and unixODBC dev packages (platform-specific). On Ubuntu 22.04:

```bash
sudo apt-get update
sudo apt-get install -y gnupg2 curl apt-transport-https
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
ACCEPT_EULA=Y sudo apt-get install -y msodbcsql17 unixodbc-dev
```

2. Start a SQL Server container:

```bash
docker run -e 'ACCEPT_EULA=Y' -e 'MSSQL_SA_PASSWORD=YourStrong!Passw0rd' -p 1433:1433 -d --name mssql-test mcr.microsoft.com/mssql/server:2019-latest
```

3. Export environment variables for the tests:

```bash
export MSSQL_TEST_SERVER=127.0.0.1
export MSSQL_TEST_DATABASE=master
export MSSQL_TEST_USERNAME=sa
export MSSQL_TEST_PASSWORD=YourStrong!Passw0rd
```

4. Install Python test deps and run the test file:

```bash
pip install pyodbc aioodbc pytest
python -m pytest -q tests/test_storage_mssql.py
```

Notes
- CI install of system ODBC drivers may need adjustment for different Ubuntu releases.
- For production-level CI, consider using a managed SQL Server instance or a self-hosted runner with the driver pre-installed.
- MSSQL integration tests are intentionally manual to avoid slowing normal PR pipelines; run them on-demand or on a schedule.
