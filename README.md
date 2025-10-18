# format-json

`format-json` is a JSON formatter that ships both a standalone CLI and a
pre-commit hook. It is adapted from the
[`pretty-format-json`](https://github.com/pre-commit/pre-commit-hooks)
pre-commit hook, with only one difference, as seen below.

**Table of Contents:**

<!--TOC-->

- [1. `format-json` vs `pretty-format-json`](#1-format-json-vs-pretty-format-json)
- [2. Usage](#2-usage)
  - [2.1. As a command-line tool](#21-as-a-command-line-tool)
  - [2.2. As a pre-commit hook](#22-as-a-pre-commit-hook)
- [3. Instructions for Maintainers](#3-instructions-for-maintainers)

<!--TOC-->

## 1. `format-json` vs `pretty-format-json`

| Feature                            | format-json | pretty-format-json                                                                      |
| ---------------------------------- | :---------: | --------------------------------------------------------------------------------------- |
| Config option for trailing newline |     ✅      | ❌ ([Won't implement ever](https://github.com/pre-commit/pre-commit-hooks/issues/1203)) |
| Preserves all digits of floats     |     ✅      | ❌ ([Unresolved since 2022](https://github.com/pre-commit/pre-commit-hooks/issues/780)) |

## 2. Usage

### 2.1. As a command-line tool

First, install it:

```bash
pip install format-json
```

Then, in the terminal, you can do something like:

```bash
format-json --autofix --no-eof-newline path/to/file.json
```

All command-line options from `pretty-format-json` are preserved, with the new
`--no-eof-newline` flag layered on top.

### 2.2. As a pre-commit hook

Add the hook to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/jsh9/format-json
  rev: <LATEST_VERSION>
  hooks:
    - id: format-json
      args: [--autofix, --no-eof-newline]
```

(You can choose your own args.)

## 3. Instructions for Maintainers

- Run `pip install -e .` to install this project in the "editable" mode.
- Run `pip install -r requirements.dev` to install developer dependencies.
- Run `pytest` to execute the automated tests replicated from the upstream
  project.
- Use `tox` to exercise the full test matrix, linting, and formatting targets.
