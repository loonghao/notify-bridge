# AGENTS.md — notify-bridge

> Navigation map, not a reference manual. Follow the links; don't read
> everything upfront.

notify-bridge is a Python notification framework: one API that sends
messages to many platforms through pluggable notifier backends.

---

## Repository Contract

**Nox is the task entrypoint; use it rather than raw pytest/ruff commands.**

| Task | Command |
|------|---------|
| Test | `nox -s pytest` |
| Lint | `nox -s lint` |
| Lint with autofix | `nox -s lint-fix` |
| Build docs | `nox -s docs` |
| Clean sessions | `nox -s clean` |

**Repository layout**

| Path | Role |
|------|------|
| `notify_bridge/` | Package — notifiers, core senders, models |
| `tests/` | pytest suite (`tests/e2e/` is separate and slower) |
| `docs/` | Documentation |
| `examples/` | Usage examples |
| `noxfile.py` | Task entrypoint |
| `uv.lock` | Locked dependency set |

**Release flow** — `release-please` on `main` drives `CHANGELOG.md` and the version in
`pyproject.toml` from Conventional Commit subjects. Tagging and PyPI
publishing run in CI. Never edit `CHANGELOG.md` or a version string by hand.

**Prohibitions**

- Do not bypass Nox for routine test/lint work.
- Do not edit `CHANGELOG.md` or version strings manually.
- Do not add a second agent contract file at the repository root; `AGENTS.md` is the single source.
- Do not commit real credentials — notifier configuration comes from the environment.

---

## Agent Contract Files

`AGENTS.md` is the **only** agent contract file at the repository root. It is the
native instruction file for Codex, OpenCode, Cursor, GitHub Copilot, Windsurf,
Cline, Roo Code, Kiro, Trae, and Augment, and Claude Code falls back to it when
no `CLAUDE.md` exists — so do not add `CLAUDE.md`, `GEMINI.md`, `CURSOR.md`, or
any other vendor-specific variant.

**Gemini CLI exception:** Gemini CLI defaults its context file to `GEMINI.md`. To
make it read `AGENTS.md`, set `context.fileName` once in `~/.gemini/settings.json`:

```json
{
  "context": {
    "fileName": ["AGENTS.md", "GEMINI.md"]
  }
}
```
