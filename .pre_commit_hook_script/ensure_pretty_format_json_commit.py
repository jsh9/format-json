#!/usr/bin/env python3
"""Ensure upstream pretty_format_json.py has not diverged."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request


EXPECTED_COMMIT = 'a49f812a96daf371c3122ee1572d1cf62da61d74'
API_URL = 'https://api.github.com/repos/pre-commit/pre-commit-hooks/commits'
FILE_PATH = 'pre_commit_hooks/pretty_format_json.py'
TIMEOUT_SECONDS = 10
MAX_ATTEMPTS = 5
BASE_BACKOFF_SECONDS = 2


def main() -> int:
    params = urllib.parse.urlencode(
        {'path': FILE_PATH, 'page': 1, 'per_page': 1},
    )
    url = f'{API_URL}?{params}'
    request = urllib.request.Request(
        url,
        headers={'User-Agent': 'format-json pre-commit hook'},
    )

    payload = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(
                request, timeout=TIMEOUT_SECONDS
            ) as resp:
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
        except urllib.error.HTTPError as exc:
            backoff = min(BASE_BACKOFF_SECONDS * attempt, 30)
            error_msg = f'HTTP {exc.code}'
            if exc.code == 403 and attempt < MAX_ATTEMPTS:
                print(
                    f'GitHub rate limit reached (attempt {attempt}/{MAX_ATTEMPTS}). '
                    f'Retrying in {backoff}s...',
                )
                time.sleep(backoff)
                continue

            if exc.code == 403:
                try:
                    reset_header = exc.headers.get('X-RateLimit-Reset')
                except AttributeError:
                    reset_header = None

                extra = ''
                if reset_header:
                    try:
                        reset_ts = int(reset_header)
                    except ValueError:
                        reset_ts = None

                    if reset_ts:
                        wait_seconds = max(reset_ts - time.time(), 0)
                        extra = f' Retry after approximately {int(wait_seconds)} seconds.'

                print(
                    f'GitHub rate limit still exceeded after retries.{extra}',
                )
                return 1

            print(
                f'Unable to reach GitHub commits API at {url}: {error_msg}',
            )
            return 1
        except urllib.error.URLError as exc:
            backoff = min(BASE_BACKOFF_SECONDS * attempt, 30)
            if attempt < MAX_ATTEMPTS:
                print(
                    f'Network error talking to GitHub ({exc.reason!r}). '
                    f'Retrying in {backoff}s...',
                )
                time.sleep(backoff)
                continue

            print(
                f'Unable to reach GitHub commits API at {url}: {exc.reason}',
            )
            return 1
        else:
            break

    if not payload:
        print(
            'Received empty commit history from GitHub; cannot verify status.'
        )
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
