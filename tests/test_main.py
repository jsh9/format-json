from __future__ import annotations

from pathlib import Path

import pytest

from format_json.main import main as format_json


def test_autofix_adds_trailing_newline_by_default(tmp_path: Path) -> None:
    input_path = tmp_path / 'test.json'
    input_path.write_text('{"foo":"bar"}', encoding='UTF-8')

    exit_code = format_json(['--autofix', str(input_path)])

    assert exit_code == 1
    assert input_path.read_text(encoding='UTF-8') == '{\n  "foo": "bar"\n}\n'


def test_autofix_respects_no_newline_flag(tmp_path: Path) -> None:
    input_path = tmp_path / 'test.json'
    input_path.write_text('{"foo":"bar"}\n', encoding='UTF-8')

    exit_code = format_json(['--autofix', '--no-eof-newline', str(input_path)])

    assert exit_code == 1
    contents = input_path.read_text(encoding='UTF-8')
    assert contents == '{\n  "foo": "bar"\n}'


def test_diff_output_when_not_autofixing(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    input_path = tmp_path / 'test.json'
    input_path.write_text('{"foo":"bar"}', encoding='UTF-8')

    exit_code = format_json([str(input_path)])

    assert exit_code == 1
    captured = capsys.readouterr().out
    assert '-{"foo":"bar"}' in captured
    assert '+  "foo": "bar"' in captured
