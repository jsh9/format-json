# format-json Agent Guide

This document distills the key facts an automated agent should know when
working with the `format-json` project. It mirrors the canonical sources
already in the repository (`README.md`, tests, and configuration files) so
agents can act independently without re-deriving project context.

## Project Snapshot

- Purpose: Provide a JSON formatter shipped both as a CLI (`format-json`) and a
  pre-commit hook.
- Unique selling point: Unlike `pretty-format-json`, this tool lets callers
  suppress the trailing newline via the `--no-eof-newline` flag while retaining
  all other upstream options.
- Distribution: Configured as a Python package with an entry point in
  `format_json/main.py`.

## Key Code Paths

- `format_json/main.py` exposes the CLI logic, including flag parsing and the
  formatter implementation.
  - `_get_pretty_format` wraps `json.dumps`, enforcing indentation, key
    sorting, optional top-level key prioritisation, UTF-8 handling, and the
    optional trailing newline.
  - `main()` iterates through provided filenames, formats them, emits diffs
    when not autofixing, and returns `0` on success, `1` when changes are
    needed, or when input JSON is invalid.
- `tests/test_main.py` covers:
  - Autofix default behaviour (adds newline).
  - The `--no-eof-newline` flag.
  - Diff output when `--autofix` is omitted.

## CLI Usage (from README)

```bash
pip install format-json
format-json --autofix --no-eof-newline path/to/file.json
```

Important flags:

- `--autofix`: Writes formatted output back to the file.
- `--indent`: Accepts either an integer or a string (e.g., `"\\t"`).
- `--no-ensure-ascii`: Keeps non-ASCII characters intact.
- `--no-sort-keys`: Preserves original key order.
- `--no-eof-newline`: Omits the trailing newline (new in this project).
- `--top-keys key1,key2`: Keeps the listed keys at the top when sorting.

## Pre-commit Hook

```yaml
- repo: https://github.com/jsh9/format-json
  rev: <LATEST_VERSION>
  hooks:
    - id: format-json
      args: [--autofix, --no-eof-newline]
```

Agents may adjust `args` as needed; the repository mirrors the upstream hook
layout so migration requires minimal changes.

## Development Workflow

- Install dev dependencies: `pip install -e .[dev]`.
- Run tests: `pytest` (configured via `pyproject.toml` to discover under
  `tests/`).
- Full suite: `tox` orchestrates the test matrix plus linting/formatting.
- Type checking: `mypy` runs in strict mode (`python_version = 3.10`).
- Additional tooling is configured in `muff.toml`, `.pre-commit-config.yaml`,
  and `tox.ini` as needed by CI.

## Release & Packaging Notes

- Packaging uses Hatch (`build-backend = "hatchling.build"`).
- Source distributions bundle code, tests, README, LICENSE, changelog, tox
  config, and hook metadata (see `pyproject.toml` for the authoritative list).
- Metadata points to the GitHub repository (`jsh9/format-json`) for homepage,
  issues, and source.

## Operational Cues for Agents

- Treat an exit code of `1` from the CLI as “changes required” rather than a
  hard failure; rerun with `--autofix` when appropriate.
- Preserve UTF-8 encoding when reading or writing JSON files.
- When modifying formatting logic, update or expand tests in
  `tests/test_main.py` to cover new scenarios.
- Keep documentation (`README.md`, `AGENTS.md`, changelog) in sync whenever
  user visible behaviour changes.
