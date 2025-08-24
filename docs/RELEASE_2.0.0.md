## Skynet Lite 2.0.0 - 2025-08-24 (Draft)

Summary
-------
Skynet Lite 2.0.0 is a records-retention focused release that introduces a retention policy engine, MSSQL compliance adapter, and a set of tools and templates for archival and export workflows. This release hardens configuration handling and includes several reliability and data-protection fixes.

Highlights
----------
- Records retention core: policy engine integration and lifecycle APIs
- MSSQL compliance adapter with schema updates and retention rules test harness
- Retention plugin templates and sample workflows for common archival patterns
- Export tooling: certified export formats, audit trails, and tamper-evident logs

Notable changes
---------------
- Refactor: retention-first processing pipeline and simplified plugin interface
- Default configuration hardened: credentials now read from environment only; examples updated
- Improved search result formatting and extractor pipelines for retention workflows

Fixes
-----
- Fixed data persistence edge-cases during concurrent archival and purge operations
- Resolved race conditions in cleanup/archival tasks
- Prevent accidental logging of sensitive configuration values

Upgrade notes
-------------
1. Backup your existing database (SQLite or other) before upgrading. If you use MSSQL, ensure you have a recent backup and read the MSSQL adapter migration notes in `docs/MSSQL_USAGE_GUIDE.md`.
2. Configuration changes:
   - `BING_API_KEY` and other removed/deprecated variables should be removed from your environment.
   - Ensure secrets are provided only through environment variables or a secret manager. Examples in `docs/` have been updated to show environment-variable usage.
3. Migration to MSSQL adapter (optional): follow `docs/MSSQL_USAGE_GUIDE.md` for schema migration and retention rules setup.

Testing & verification
----------------------
1. Run the test suite (pytest) and the `web/test_web.py` integration tests.
2. Validate retention workflows by running the retention rules test harness under `scripts/`.
3. Verify export tool output and audit trail metadata for tamper-evidence.

Contact
-------
If you run into issues during upgrade, open an issue on this repository and include the following information:
- Skynet Lite version before upgrade
- Database type and version
- A short reproducible test case or the failing log snippets

This is a draft release note — please review and confirm the messaging, then I'll create the GitHub release and tag.
