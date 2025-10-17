#!/usr/bin/env python3
"""Ensure upstream pretty_format_json.py has not diverged."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request


EXPECTED_COMMIT = 'a49f812a96daf371c3122ee1572d1cf62da61d74'
API_URL = 'https://api.github.com/repos/pre-commit/pre-commit-hooks/commits'
FILE_PATH = 'pre_commit_hooks/pretty_format_json.py'
TIMEOUT_SECONDS = 10


def main() -> int:
    params = urllib.parse.urlencode(
        {'path': FILE_PATH, 'page': 1, 'per_page': 1},
    )
    url = f'{API_URL}?{params}'
    request = urllib.request.Request(
        url,
        headers={'User-Agent': 'format-json pre-commit hook'},
    )

    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as resp:
            if resp.status != 200:
                print(
                    'Failed to query GitHub commits API; '
                    f'expected HTTP 200 but received {resp.status}.',
                )
                return 1
            try:
                payload = json.load(resp)
            except json.JSONDecodeError as exc:
                print(f'Unable to parse response from GitHub: {exc}')
                return 1
    except urllib.error.URLError as exc:
        print(f'Unable to reach GitHub commits API at {url}: {exc.reason}')
        return 1

    if not payload:
        print('Received empty commit history from GitHub; cannot verify status.')
        return 1

    latest_commit = payload[0]['sha']
    if latest_commit != EXPECTED_COMMIT:
        print(
            'pre_commit_hooks/pretty_format_json.py has changed upstream.\n'
            f'  Expected latest commit: {EXPECTED_COMMIT}\n'
            f'  Observed latest commit: {latest_commit}\n'
            'Please review upstream changes and update format-json accordingly.',
        )
        return 1

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
