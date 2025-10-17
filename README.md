# format-json

`format-json` is a JSON formatter that ships both a standalone CLI and a
pre-commit hook. It is adapted from the
[`pretty-format-json`](https://github.com/pre-commit/pre-commit-hooks)
pre-commit hook, with only one difference, as seen below.

## How this differs from `pretty-format-json`

`format-json` has an extra config option `--no-eof-newline` to control whether
a trailing newline is appended to formatted JSON output.

## Why a separate project?

The maintainers of `pretty-format-json` chose not to add a configuration option
for controlling trailing newlines, but there are oftentimes practical reasons
for JSON files to not have a trailing newline.

## As a command-line tool

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

## As a pre-commit hook

Add the hook to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/jsh9/format-json
  rev: <LATEST_VERSION>
  hooks:
    - id: format-json
      args: [--autofix, --no-eof-newline]
```

(You can choose your own args.)

## Development

- Run `pip install -e .[dev]` to install development dependencies.
- Run `pytest` to execute the automated tests replicated from the upstream
  project.
- Use `tox` to exercise the full test matrix, linting, and formatting targets.
