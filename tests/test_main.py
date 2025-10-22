# Adapted from https://github.com/pre-commit/pre-commit-hooks/blob/3fed74c572621f74eaffba6603801d153ffe5ce0/tests/pretty_format_json_test.py

import os
import shutil
from pathlib import Path

import pytest

from format_json.main import main, parse_num_to_int

RESOURCE_DIR = os.path.abspath(os.path.dirname(__file__))


def get_resource_path(path: str) -> str:
    return os.path.join(RESOURCE_DIR, 'test_data', path)


def test_parse_num_to_int() -> None:
    assert parse_num_to_int('0') == 0
    assert parse_num_to_int('2') == 2
    assert parse_num_to_int('\t') == '\t'
    assert parse_num_to_int('  ') == '  '


@pytest.mark.parametrize(
    ('filename', 'expected_retval'),
    [
        ('not_pretty_formatted_json.json', 1),
        ('unsorted_pretty_formatted_json.json', 1),
        ('non_ascii_pretty_formatted_json.json', 1),
        ('pretty_formatted_json.json', 0),
        ('pretty_formatted_json_no_eof_newline.json', 1),
        ('high_precision_float_formatted.json', 0),
    ],
)
def test_main(filename: str, expected_retval: int) -> None:
    ret = main([get_resource_path(filename)])
    assert ret == expected_retval


@pytest.mark.parametrize(
    ('filename', 'expected_retval'),
    [
        ('not_pretty_formatted_json.json', 1),
        ('unsorted_pretty_formatted_json.json', 0),
        ('non_ascii_pretty_formatted_json.json', 1),
        ('pretty_formatted_json.json', 0),
        ('high_precision_float_formatted.json', 0),
    ],
)
def test_unsorted_main(filename: str, expected_retval: int) -> None:
    ret = main(['--no-sort-keys', get_resource_path(filename)])
    assert ret == expected_retval


@pytest.mark.parametrize(
    ('filename', 'expected_retval'),
    [
        ('not_pretty_formatted_json.json', 1),
        ('unsorted_pretty_formatted_json.json', 1),
        ('non_ascii_pretty_formatted_json.json', 1),
        ('pretty_formatted_json.json', 1),
        ('tab_pretty_formatted_json.json', 0),
    ],
)
def test_tab_main(filename: str, expected_retval: int) -> None:
    ret = main(['--indent', '\t', get_resource_path(filename)])
    assert ret == expected_retval


def test_non_ascii_main() -> None:
    ret = main((
        '--no-ensure-ascii',
        get_resource_path('non_ascii_pretty_formatted_json.json'),
    ))
    assert ret == 0


def test_autofix_main(tmp_path: Path) -> None:
    srcfile = tmp_path / 'to_be_json_formatted.json'
    shutil.copyfile(
        get_resource_path('not_pretty_formatted_json.json'),
        srcfile,
    )

    # now launch the autofix on that file
    ret = main(['--autofix', str(srcfile)])
    # it should have formatted it
    assert ret == 1

    # file was formatted (shouldn't trigger linter again)
    ret = main([str(srcfile)])
    assert ret == 0


@pytest.mark.parametrize(
    ('extra_args', 'expect_newline'),
    [
        ((), True),
        (('--no-eof-newline',), False),
    ],
)
def test_no_eof_newline_behavior(
        tmp_path: Path,
        extra_args: tuple[str, ...],
        expect_newline: bool,  # noqa: FBT001
) -> None:
    srcfile = tmp_path / 'newline_behavior.json'
    shutil.copyfile(
        get_resource_path('not_pretty_formatted_json.json'),
        srcfile,
    )

    ret = main(['--autofix', *extra_args, str(srcfile)])
    assert ret == 1

    contents = srcfile.read_text()
    if expect_newline:
        assert contents.endswith('\n')
        assert not contents.endswith('\n\n')
    else:
        assert contents.endswith('}')
        assert not contents.endswith('\n')

    check_args = [*extra_args, str(srcfile)]
    assert main(check_args) == 0


def test_no_eof_newline_already_formatted() -> None:
    ret = main((
        '--no-eof-newline',
        get_resource_path('pretty_formatted_json_no_eof_newline.json'),
    ))
    assert ret == 0


def test_invalid_main(tmp_path: Path) -> None:
    srcfile1 = tmp_path / 'not_valid_json.json'
    srcfile1.write_text(
        '{\n  // not json\n  "a": "b"\n}',
    )
    srcfile2 = tmp_path / 'to_be_json_formatted.json'
    srcfile2.write_text('{ "a": "b" }')

    # it should have skipped the first file and formatted the second one
    assert main(['--autofix', str(srcfile1), str(srcfile2)]) == 1

    # confirm second file was formatted (shouldn't trigger linter again)
    assert main([str(srcfile2)]) == 0


def test_orderfile_get_pretty_format() -> None:
    ret = main((
        '--top-keys=alist',
        get_resource_path('pretty_formatted_json.json'),
    ))
    assert ret == 0


def test_not_orderfile_get_pretty_format() -> None:
    ret = main((
        '--top-keys=blah',
        get_resource_path('pretty_formatted_json.json'),
    ))
    assert ret == 1


def test_top_sorted_get_pretty_format() -> None:
    ret = main((
        '--top-keys=01-alist,alist',
        get_resource_path('top_sorted_json.json'),
    ))
    assert ret == 0


def test_badfile_main() -> None:
    ret = main([get_resource_path('ok_yaml.yaml')])
    assert ret == 1


def test_diffing_output(capsys: pytest.CaptureFixture[str]) -> None:
    resource_path = get_resource_path('not_pretty_formatted_json.json')
    expected_retval = 1
    a = os.path.join('a', resource_path)
    b = os.path.join('b', resource_path)
    expected_out = f"""\
--- {a}
+++ {b}
@@ -1,6 +1,9 @@
 {{
-    "foo":
-    "bar",
-        "alist": [2, 34, 234],
-  "blah": null
+  "alist": [
+    2,
+    34,
+    234
+  ],
+  "blah": null,
+  "foo": "bar"
 }}
"""
    actual_retval = main([resource_path])
    actual_out, actual_err = capsys.readouterr()

    assert actual_retval == expected_retval
    assert actual_out == expected_out
    assert actual_err == ''
