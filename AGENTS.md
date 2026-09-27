# AGENTS.md — notify-bridge

> Pure-Python async library and CLI that sends notifications to multiple
> platforms (Feishu, WeCom, GitHub, generic Notify) through one `Notifier`
> interface, with a plugin system for third-party notifiers.
> Navigation map for AI agents, not a reference manual. Follow the links; do
> not read everything up front.

## Build & test

No justfile. CI installs with `uv` and drives everything through nox
(`noxfile.py` sessions: `pytest`, `lint`, `lint-fix`, `docs`, `clean`).

```bash
python -m pip install uv
uv venv
source .venv/bin/activate          # Windows: source .venv/Scripts/activate
uv pip install -r requirements-dev.txt
pre-commit install
```

```bash
nox -s pytest -- tests/ --ignore=tests/e2e/ -v   # unit tests (what CI runs)
nox -s pytest -- tests/notify_bridge/test_core.py -v   # one file
nox -s lint                        # autoflake, ruff, black, mypy
nox -s lint-fix                    # autofix variants of the same checks
nox -s docs                        # build the docs site
nox -s clean                       # remove build/test artifacts
```

Plain `pytest` also works after `pip install -e ".[dev]"` — `pyproject.toml`
already sets `addopts = "-v --cov=notify_bridge --cov-report=term-missing"` and
`asyncio_mode = "strict"`.

E2E tests (`tests/e2e/`) hit real webhook endpoints and are gated on secrets —
they run only for same-repository pull requests. Do not run them locally
without the required environment variables.

## Repo layout

| Path | Role |
|---|---|
| `notify_bridge/core.py` | `Notifier` base class and the sync/async send entry points |
| `notify_bridge/components.py` | Reusable message component builders |
| `notify_bridge/schema.py` | Pydantic message and response models |
| `notify_bridge/factory.py` | Notifier construction and lookup |
| `notify_bridge/plugin.py` | Plugin discovery via the `notify_bridge.notifiers` entry point |
| `notify_bridge/notifiers/` | `feishu.py`, `wecom.py`, `github.py`, `notify.py` |
| `notify_bridge/exceptions.py`, `utils.py` | Error types and helpers |
| `tests/` | Unit tests (`test_core.py`, `test_components.py`, `test_factory.py`, `test_plugin.py`, `test_utils.py`), `tests/notify_bridge/`, and `tests/e2e/` |
| `docs/` | `index.md`, `guide/` (getting-started, feishu, wecom, github, plugins, error-handling), `api/`, `zh/` |
| `examples/` | Runnable per-platform samples |
| `noxfile.py`, `.pre-commit-config.yaml` | Task runner and pre-commit hooks |
| `pyproject.toml` | `pdm-backend` build; `[tool.pytest.ini_options]`, ruff, mypy, black, isort config |

## Release

- release-please drives versioning from Conventional Commits on `main`
  (`release-please-config.json`).
  `.release-please-manifest.json` is the single source of version truth.
- `feat:` → minor, `fix:` → patch, `chore:`/`docs:`/`ci:` → **no release**.
- Use `chore:`/`docs:` for config and doc work so release-please does not cut a
  valueless version.
- Merging the release PR creates the GitHub release and tag; the PyPI publish
  is handled by `.github/workflows/release.yml`. A separate
  `version-consistency.yml` workflow guards against version drift.

## Do / Don't

- **Do** register a new notifier as an entry point under
  `[project.entry-points."notify_bridge.notifiers"]` so `plugin.py` can
  discover it.
- **Do** keep the sync and async send paths in `core.py` in step — both are
  part of the public surface.
- **Do** match the existing style gates: line-length 120, `asyncio_mode =
  "strict"`, annotated public functions (mypy `disallow_untyped_defs = true`).
- **Don't** add network calls to the unit test suite; put them in `tests/e2e/`.
- **Don't** hardcode an exact version in tests (`assert __version__ == "X.Y.Z"`)
  — release-please bumps will break it. Use `>=` or read package metadata.
- **Don't** add `CLAUDE.md` / `GEMINI.md` / `CURSOR.md` / `ANTHROPIC.md` /
  `OPENAI.md` / `COPILOT.md` / `CODEBUDDY.md` / `.cursorrules` / `.clinerules` /
  `.windsurfrules` at the root. This file is the only agent contract file.
- **Don't** commit build artifacts to the repo root (`dist/`, `build/`,
  `.coverage`, `coverage.xml`, `htmlcov/`).
