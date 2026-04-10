Fix the bug in `src/normalize_port.py` so `65535` is accepted as a valid port.

Run `python -m pytest -q tests/test_normalize_port.py`.

Keep this lane minimal. Do not widen the task into extra cleanup, extra proof
work, or new tests unless the target test forces a small local change.

At the end, report only the files you actually changed and the test command you
actually ran.
