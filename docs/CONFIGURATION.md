# Configuration (skynet.config)

This project uses a packaged configuration object available as `from skynet.config import Config`.
The implementation prefers the modern `pydantic-settings` API when available, falls back to `pydantic` types,
and includes a plain-Python fallback so the library remains usable in minimal environments.

This document explains the configuration options, environment-variable mappings, `.env` support, and
convenience helpers introduced for migration and setup.

## Quick summary

- Primary import: `from skynet.config import Config`
- Config reads values from environment variables and from a `.env` file if present (via pydantic-settings).
- A helper `Config.create_default_config_file(path='config.yaml')` is available to generate a simple
  `config.yaml` with current defaults for quick setup.
- The previous top-level `config.py` shim has been removed in favor of the package import. If you depended on
  `from config import Config`, update your code to `from skynet.config import Config`.

## Available settings

The following settings are exposed by `Config` and their default values:

- `ollama_model` (env: `OLLAMA_MODEL`) — default: `mistral`
- `search_provider` (env: `SEARCH_PROVIDER`) — default: `duckduckgo`
- `search_use_instant_answers` (env: `SEARCH_USE_INSTANT_ANSWERS`) — default: `True`

These are intentionally lightweight and intended as the core options used across the project. The `Config`
implementation accepts additional fields if you extend it in your own deployments.

## Examples

Example: load configuration in code

```python
from skynet.config import Config

cfg = Config()
print(cfg.ollama_model)
```

Use environment variables (Bash):

```bash
export OLLAMA_MODEL=mistral-7b
export SEARCH_PROVIDER=bing
export SEARCH_USE_INSTANT_ANSWERS=0
```

`.env` file example (placed at repo root):

```
OLLAMA_MODEL=mistral-7b
SEARCH_PROVIDER=duckduckgo
SEARCH_USE_INSTANT_ANSWERS=1
```

Create a default `config.yaml` with Python (uses `Config.create_default_config_file`):

```python
from skynet.config import Config

cfg = Config()
cfg.create_default_config_file('config.yaml')
```

Or from the repo root using the interactive Python shell:

```bash
python -c "from skynet.config import Config; Config().create_default_config_file()"
```

## Migration notes

- The repository previously provided a top-level `config.py` shim that allowed `from config import Config`.
  That shim was removed to enforce the package namespace. Update external scripts and tooling to import
  `skynet.config` instead.
- The new `Config` implementation prefers `pydantic-settings` (recommended). If `pydantic-settings` is
  not installed, the code falls back to `pydantic` or to a plain-Python implementation to keep things working.

## Requirements and recommendations

- Recommended installation (development / production) should include `pydantic` and `pydantic-settings`.
  These are added to the repository `requirements.txt` and `main/requirements.txt`.
- If you use `.env` files, keep them out of version control and secure any secrets (API keys, etc.).

## Environment variables used by other components

- `BING_API_KEY` — optional environment variable used by setup and search integration if you configure
  Bing web search.

## Troubleshooting

- If `from skynet.config import Config` raises an ImportError:
  - Ensure you are running within the repository (the package is importable) and your `PYTHONPATH` includes the repo root.
  - Make sure dependencies are installed in your environment (see `requirements.txt`).
- If you see warnings about pydantic migration/deprecations, upgrade to the latest `pydantic` and `pydantic-settings`.

## Further improvements you can make

- Convert the default `create_default_config_file` output to proper YAML using `pyyaml` (the project already
  depends on `pyyaml`). This is low-risk and improves interoperability with other tooling.
- Centralize configuration schema in one place (extend `Config` with additional fields used project-wide).


